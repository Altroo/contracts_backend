"""Small typed registry over existing Contracts models, filters and native views."""
from datetime import date, timedelta
import time
from django.conf import settings
from django.db import connection, transaction, OperationalError
from django.db.models import Q
from django.utils import timezone
from chat_ai_assistant.contracts import ChatAIError, ChatAITool, ChatAIToolRegistry, object_schema, ID, STRING
from core.constants import STATUT_CHOICES, CONTRACT_CATEGORY_CHOICES, CURRENCY_CHOICES
from .security import authorize, capabilities, company_code
from .resources import RESOURCES
from .models import AuditEvent
from .navigation import ChatAINavigationResolver, ROUTES, DETAILS
from .labels import FIELD_LABELS, FIELD_LABELS_EN
from .knowledge import ChatAIKnowledgeService

RESOURCE = {"type": "string", "enum": list(RESOURCES)}
DATE = {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
SEARCH = object_schema({
    "resource": RESOURCE, "query": STRING, "client_name": STRING,
    "subcontractor_name": STRING, "project_name": STRING,
    "status": {"type": "string", "enum": [v for v, _ in STATUT_CHOICES]},
    "category": {"type": "string", "enum": [v for v, _ in CONTRACT_CATEGORY_CHOICES]},
    "currency": {"type": "string", "enum": [v for v, _ in CURRENCY_CHOICES]},
    "date_from": DATE, "date_to": DATE,
    "limit": {"type": "integer", "minimum": 1, "maximum": 10},
    "offset": {"type": "integer", "minimum": 0, "maximum": 100},
}, ["resource"])


def registry():
    specifications = [
        ("search_records", "Find contracts, construction projects or permitted users by description. Contract filters combine with AND.", SEARCH, ("read",)),
        ("get_record", "Read a known internal identifier or current-page record; contract numbers require search.", object_schema({"resource": RESOURCE, "identifier": ID}, ["resource"]), ("read",)),
        ("navigate", "Open a permitted native list, known detail, edit or creation form. No project detail page exists.", object_schema({"resource": {"type": "string", "enum": list(ROUTES) + list(DETAILS) + [r + suffix for r in DETAILS for suffix in ("_edit", "_new")]}, "identifier": ID}, ["resource"]), ("read",)),
        ("knowledge", "Retrieve verified application procedures, statuses and financial terminology.", object_schema({"query": STRING}, ["query"]), ("read",)),
        ("previous_results", "List saved results or open a known result by one-based index.", object_schema({"operation": {"type": "string", "enum": ["open", "list"]}, "index": {"type": "integer", "minimum": 1, "maximum": 10}}, ["operation"]), ("read",)),
        ("contract_document", "Offer the native PDF or Word document of a known contract; fresh print permission required.", object_schema({"identifier": ID, "format": {"type": "string", "enum": ["pdf", "docx"]}, "language": {"type": "string", "enum": ["fr", "en"]}}, ["identifier", "format", "language"]), ("read", "print")),
        ("prepare_change", "Propose a known contract/project edit or deletion for separate exact-target user confirmation; never executes.", object_schema({"resource": {"type": "string", "enum": [r for r, spec in RESOURCES.items() if spec.editable]}, "identifier": ID, "operation": {"type": "string", "enum": ["update", "delete"]}, "changes": {"type": "object", "maxProperties": 8, "propertyNames": {"enum": sorted({f for spec in RESOURCES.values() for f in spec.editable})}, "additionalProperties": {"type": ["string", "null"], "maxLength": 1000}}}, ["resource", "identifier", "operation"]), ("read",)),
    ]
    return ChatAIToolRegistry([ChatAITool(name, description, schema, {"type": "object"}, name, application="contrat", required_capabilities=caps, authorization="fresh native flags, staff checks and selected-company scope", classification="proposal" if name == "prepare_change" else "read", audit_classification="business_proposal" if name == "prepare_change" else "business_read") for name, description, schema, caps in specifications])


class ChatAIToolExecutor:
    def __init__(self, user_id, company_id, request_id, state=None, context=None, audit=True, instruction=None):
        self.user_id, self.company_id, self.request_id = user_id, company_id, request_id
        self.state, self.context = state or {}, context or {}
        self.audit, self.instruction = audit, instruction

    def authorize(self):
        return authorize(self.user_id, self.company_id)

    authorize_context = authorize

    def capabilities(self):
        return capabilities(self.authorize())

    def output_labels(self):
        return FIELD_LABELS_EN if self.context.get("interface_language") == "en" else FIELD_LABELS

    def authorize_knowledge(self, documents):
        sources = [{"document_id": d["document_id"], "version": d["version"]} for d in documents]
        if not ChatAIKnowledgeService.sources_authorized(sources, self.company_id, self.capabilities()):
            raise ChatAIError("CONTEXT_EXPIRED")

    def execute(self, name, arguments):
        started, outcome = time.monotonic(), "denied"
        try:
            self.authorize()
            tool = registry().validate(name, arguments)
            if not set(tool.required_capabilities) <= self.capabilities():
                raise ChatAIError("PERMISSION_DENIED")
            try:
                with transaction.atomic():
                    if connection.vendor == "postgresql":
                        with connection.cursor() as cursor:
                            cursor.execute("SET LOCAL statement_timeout = %s", [tool.timeout_seconds * 1000])
                    result = getattr(self, name)(**arguments)
                    if time.monotonic() - started > tool.timeout_seconds:
                        raise ChatAIError("TOOL_TIMEOUT")
                    self.authorize()
            except OperationalError as exc:
                if getattr(exc.__cause__, "pgcode", None) in ("57014", "55P03"):
                    raise ChatAIError("TOOL_TIMEOUT") from None
                raise
            outcome = "allowed"
            return result
        finally:
            if self.audit:
                AuditEvent.objects.create(user_id=self.user_id, actor_id=self.user_id, company_id=self.company_id, application="contrat", tool=name[:64], outcome=outcome, correlation_id=self.request_id, model_version=settings.CHAT_AI_MODEL_ID, duration_ms=max(0, int((time.monotonic() - started) * 1000)))

    def queryset(self, resource):
        self.authorize()
        if resource not in RESOURCES:
            raise ChatAIError("INVALID_ARGUMENTS")
        if resource == "user":
            if "users_read" not in self.capabilities():
                raise ChatAIError("PERMISSION_DENIED")
            return RESOURCES[resource].model.objects.all()
        return RESOURCES[resource].model.objects.filter(company=company_code(self.company_id))

    def record(self, resource, identifier):
        if type(identifier) is not int or not 0 < identifier <= 2147483647:
            raise ChatAIError("INVALID_ARGUMENTS")
        item = self.queryset(resource).filter(pk=identifier).first()
        if item is None:
            raise ChatAIError("NOT_FOUND")
        return item

    def serialize(self, resource, obj):
        if resource == "contract":
            item = {"id": obj.pk, "name": obj.numero_contrat, "client": (obj.client_nom or obj.st_name or "")[:200], "status": obj.get_statut_display(), "date": obj.date_contrat.isoformat(), "amount": str(obj.montant_ttc), "currency": obj.devise, "details": [
                {"label": "Montant total HT", "label_en": "Total excluding tax", "value": str(obj.montant_ht) + " " + obj.devise},
                {"label": "TVA (%)", "label_en": "VAT (%)", "value": str(obj.tva)},
                {"label": "Catégorie de contrat", "label_en": "Contract category", "value": obj.get_contract_category_display()},
            ]}
            if obj.description_travaux:
                item["description"] = obj.description_travaux[:400]
            if obj.st_projet_id and obj.st_projet.company == company_code(self.company_id):
                item["project"] = obj.st_projet.name[:300]
        elif resource == "project":
            item = {"id": obj.pk, "name": obj.name[:300], "description": (obj.description or "")[:400]}
        else:
            if "users_read" not in self.capabilities():
                raise ChatAIError("PERMISSION_DENIED")
            item = {"id": obj.pk, "name": str(obj)[:200], "status": "Actif" if obj.is_active else "Inactif"}
        if resource in ("contract", "project"):
            caps = self.capabilities()
            item["can_update"] = "update" in caps
            item["can_delete"] = "delete" in caps and (resource != "project" or (not obj.is_predefined and not obj.contracts.exclude(company=obj.company).exists()))
        if resource in DETAILS:
            item["navigation"] = ChatAINavigationResolver.resolve(resource, self.company_id, obj.pk)
        return item

    def read_records(self, resource, ids):
        if not isinstance(ids, list) or len(ids) > 10 or any(type(i) is not int or i < 1 for i in ids):
            raise ChatAIError("INVALID_ARGUMENTS")
        objects = {obj.pk: obj for obj in self.queryset(resource).filter(pk__in=ids)}
        return [self.serialize(resource, objects[i]) for i in ids if i in objects]

    def search_records(self, resource, query="", client_name="", subcontractor_name="", project_name="", status="", category="", currency="", date_from=None, date_to=None, limit=10, offset=0):
        qs = self.queryset(resource)
        try:
            dates = [date.fromisoformat(v) for v in (date_from, date_to) if v]
        except ValueError:
            raise ChatAIError("INVALID_ARGUMENTS") from None
        if len(dates) == 2 and dates[0] > dates[1]:
            raise ChatAIError("INVALID_ARGUMENTS")
        if resource == "contract":
            params = {"statut": status, "contract_category": category, "devise": currency, "date_after": date_from, "date_before": date_to}
            filters = RESOURCES[resource].filterset({k: v for k, v in params.items() if v}, queryset=qs)
            if not filters.is_valid():
                raise ChatAIError("INVALID_ARGUMENTS")
            qs = filters.qs
            if query:
                qs = qs.filter(Q(numero_contrat__icontains=query) | Q(client_nom__icontains=query) | Q(st_name__icontains=query) | Q(adresse_travaux__icontains=query) | Q(description_travaux__icontains=query) | Q(st_lot_description__icontains=query))
            if client_name:
                qs = qs.filter(client_nom__icontains=client_name)
            if subcontractor_name:
                qs = qs.filter(st_name__icontains=subcontractor_name)
            if project_name:
                qs = qs.filter(st_projet__company=company_code(self.company_id), st_projet__name__icontains=project_name)
            qs = qs.order_by("-date_contrat", "-id")
        else:
            if any((client_name, subcontractor_name, project_name, status, category, currency, date_from, date_to)):
                raise ChatAIError("INVALID_ARGUMENTS")
            if query:
                fields = ("name", "description", "adresse") if resource == "project" else ("first_name", "last_name", "email")
                match = Q()
                for field in fields:
                    match |= Q(**{field + "__icontains": query})
                qs = qs.filter(match)
            qs = qs.order_by("-id")
        found = list(qs[offset:offset + limit + 1])
        items = [self.serialize(resource, obj) for obj in found[:limit]]
        self.state = {"resource": resource, "ids": [x["id"] for x in items], "expires_at": (timezone.now() + timedelta(minutes=20)).isoformat()}
        return {"type": "record_list", "resource": resource, "items": items, "has_more": len(found) > limit}

    def get_record(self, resource, identifier=None):
        if identifier is None:
            if self.context.get("resource") != resource:
                raise ChatAIError("INVALID_ARGUMENTS")
            identifier = self.context.get("identifier")
        obj = self.record(resource, identifier)
        self.state = {"resource": resource, "ids": [obj.pk], "expires_at": (timezone.now() + timedelta(minutes=20)).isoformat()}
        return {"type": "record_list", "resource": resource, "items": [self.serialize(resource, obj)]}

    def navigate(self, resource, identifier=None):
        caps = self.capabilities()
        base = resource.removesuffix("_new").removesuffix("_edit")
        if base in ("users", "user") and "users_read" not in caps:
            raise ChatAIError("PERMISSION_DENIED")
        if resource.endswith("_new"):
            if "create" not in caps:
                raise ChatAIError("PERMISSION_DENIED")
        elif resource.endswith("_edit"):
            if "update" not in caps:
                raise ChatAIError("PERMISSION_DENIED")
            self.record(base, identifier)
        elif base in DETAILS:
            self.record(base, identifier)
        return {"type": "navigation", "target": ChatAINavigationResolver.resolve(resource, self.company_id, identifier)}

    def previous_results(self, operation, index=None):
        if not self.state.get("ids") or self.state.get("expires_at", "") < timezone.now().isoformat():
            raise ChatAIError("CONTEXT_EXPIRED")
        resource = self.state["resource"]
        items = self.read_records(resource, self.state["ids"])
        if len(items) != len(self.state["ids"]):
            raise ChatAIError("CONTEXT_EXPIRED")
        if operation == "list":
            return {"type": "record_list", "resource": resource, "items": items}
        if index is None or index > len(items) or not items[index - 1].get("navigation"):
            raise ChatAIError("INVALID_ARGUMENTS")
        return {"type": "navigation", "target": items[index - 1]["navigation"]}

    def knowledge(self, query):
        return {"type": "knowledge", "documents": ChatAIKnowledgeService().retrieve(query, self.company_id, self.capabilities())}

    def contract_document(self, identifier, format, language):
        if "print" not in self.capabilities():
            raise ChatAIError("PERMISSION_DENIED")
        obj = self.record("contract", identifier)
        if obj.st_projet_id and obj.st_projet.company != company_code(self.company_id):
            raise ChatAIError("NOT_FOUND")
        return {"type": "pdf", "resource": "contract", "record_id": obj.pk, "number": obj.numero_contrat, "format": format, "language": language}

    def prepare_change(self, resource, identifier, operation, changes=None):
        from .actions import prepare
        return prepare(self, resource, identifier, operation, changes or {})
