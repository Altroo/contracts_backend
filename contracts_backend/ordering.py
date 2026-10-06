"""Allowlisted public column ordering, before pagination or list serialization."""

from django.db.models import Case, CharField, F, TextField, Value, When
from django.db.models.functions import Lower


def direct(names):
    return {name: F(name) for name in names.split()}


def fields_for(queryset, field, params):
    model = queryset.model._meta.label_lower
    fields = {
        "accounts.customuser": direct(
            "first_name last_name email gender is_staff is_active date_joined last_login"
        )
    }
    fields["contract.contract"] = direct(
        "numero_contrat client_nom company contract_category statut date_contrat montant_ht"
    )
    if model == "contract.contract":
        for public, source in [
            ("type_contrat_display", "type_contrat"),
            ("company", "company"),
            ("contract_category", "contract_category"),
        ]:
            choices = queryset.model._meta.get_field(source).choices
            fields[model][public] = Case(
                *[
                    When(**{source: value}, then=Value(str(label)))
                    for value, label in choices
                ],
                default=F(source),
                output_field=CharField()
            )
    return queryset, fields.get(model, {})


def apply_list_ordering(queryset, params):
    ordering = params.get("ordering", "")
    if not ordering or not hasattr(queryset, "model"):
        return queryset
    descending = ordering.startswith("-")
    field = ordering[1:] if descending else ordering
    queryset, fields = fields_for(queryset, field, params)
    expression = fields.get(field)
    if expression is None:
        return queryset
    resolved = expression.resolve_expression(queryset.query)
    if isinstance(resolved.output_field, (CharField, TextField)):
        expression = Lower(expression)
    queryset = queryset.alias(_list_ordering_value=expression)
    order = F("_list_ordering_value")
    return queryset.order_by(
        order.desc(nulls_last=True) if descending else order.asc(nulls_last=True),
        "-pk" if descending else "pk",
    )
