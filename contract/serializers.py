from decimal import Decimal, InvalidOperation

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import Contract, Project
from core.constants import ST_LOT_TYPE_CHOICES, ST_TYPE_PRIX_CHOICES

_VALID_LOT_TYPES = {code for code, _ in ST_LOT_TYPE_CHOICES}
_VALID_TYPE_PRIX = {code for code, _ in ST_TYPE_PRIX_CHOICES}

ECHEANCIER_TOTAL_ERROR = _(
    "Le total des pourcentages de l'échéancier doit être égal à 100%."
)


def _has_valid_echeancier_total(tranches) -> bool:
    if not isinstance(tranches, list):
        return False

    total = Decimal("0")
    for tranche in tranches:
        if not isinstance(tranche, dict):
            return False

        try:
            total += Decimal(str(tranche.get("pourcentage", 0) or 0))
        except (InvalidOperation, TypeError, ValueError):
            return False

    return total == Decimal("100")


class ProjectSerializer(serializers.ModelSerializer):
    """Full serializer for Project CRUD."""

    type_display = serializers.CharField(source="get_type_display", read_only=True)
    company_display = serializers.CharField(
        source="get_company_display", read_only=True
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "company",
            "company_display",
            "name",
            "type",
            "type_display",
            "description",
            "adresse",
            "maitre_ouvrage",
            "permis",
            "is_predefined",
            "created_by_user",
            "date_created",
            "date_updated",
        ]
        read_only_fields = [
            "id",
            "company_display",
            "type_display",
            "created_by_user",
            "date_created",
            "date_updated",
        ]


class ContractListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the contract list view."""

    client_name = serializers.SerializerMethodField()
    created_by_user_name = serializers.SerializerMethodField()
    montant_tva = serializers.SerializerMethodField()
    montant_ttc = serializers.SerializerMethodField()
    type_contrat_display = serializers.CharField(
        source="get_type_contrat_display", read_only=True
    )
    statut_display = serializers.CharField(source="get_statut_display", read_only=True)
    company_display = serializers.CharField(
        source="get_company_display", read_only=True
    )
    contract_category_display = serializers.CharField(
        source="get_contract_category_display", read_only=True
    )

    @staticmethod
    def get_client_name(obj: Contract) -> str | None:
        return obj.client_nom

    @staticmethod
    def get_created_by_user_name(obj: Contract) -> str | None:
        if obj.created_by_user:
            name = f"{obj.created_by_user.first_name} {obj.created_by_user.last_name}".strip()
            return name or obj.created_by_user.email
        return None

    @staticmethod
    def get_montant_tva(obj: Contract) -> float:
        return obj.montant_tva

    @staticmethod
    def get_montant_ttc(obj: Contract) -> float:
        return obj.montant_ttc

    class Meta:
        model = Contract
        fields = [
            "id",
            "numero_contrat",
            "company",
            "company_display",
            "contract_category",
            "contract_category_display",
            "client_name",
            "client_nom",
            "date_contrat",
            "type_contrat",
            "type_contrat_display",
            "statut",
            "statut_display",
            "montant_ht",
            "tva",
            "montant_tva",
            "montant_ttc",
            "devise",
            "confidentialite",
            "created_by_user",
            "created_by_user_name",
            "date_created",
            "date_updated",
        ]
        read_only_fields = fields


class ContractSerializer(serializers.ModelSerializer):
    """Full serializer for contract create / retrieve / update."""

    client_name = serializers.SerializerMethodField(read_only=True)
    created_by_user_name = serializers.SerializerMethodField(read_only=True)
    created_by_user_id = serializers.IntegerField(
        source="created_by_user.id", read_only=True
    )
    montant_tva = serializers.SerializerMethodField(read_only=True)
    montant_ttc = serializers.SerializerMethodField(read_only=True)
    type_contrat_display = serializers.CharField(
        source="get_type_contrat_display", read_only=True
    )
    company_display = serializers.CharField(
        source="get_company_display", read_only=True
    )
    contract_category_display = serializers.CharField(
        source="get_contract_category_display", read_only=True
    )
    solde = serializers.SerializerMethodField(read_only=True)
    st_projet_detail = ProjectSerializer(source="st_projet", read_only=True)

    @staticmethod
    def get_client_name(obj: Contract) -> str | None:
        return obj.client_nom

    @staticmethod
    def get_created_by_user_name(obj: Contract) -> str | None:
        if obj.created_by_user:
            name = f"{obj.created_by_user.first_name} {obj.created_by_user.last_name}".strip()
            return name or obj.created_by_user.email
        return None

    @staticmethod
    def get_montant_tva(obj: Contract) -> float:
        return obj.montant_tva

    @staticmethod
    def get_montant_ttc(obj: Contract) -> float:
        return obj.montant_ttc

    @staticmethod
    def get_solde(obj: Contract) -> float:
        return obj.solde

    def validate_st_lot_type(self, value):
        if value is None:
            return value
        if not isinstance(value, list):
            raise serializers.ValidationError(_("La valeur doit être une liste."))
        invalid = [v for v in value if v not in _VALID_LOT_TYPES]
        if invalid:
            raise serializers.ValidationError(
                _("Valeur(s) invalide(s) : %(values)s") % {"values": ", ".join(invalid)}
            )
        return value

    def validate_st_type_prix(self, value):
        if value is None:
            return value
        if not isinstance(value, list):
            raise serializers.ValidationError(_("La valeur doit être une liste."))
        invalid = [v for v in value if v not in _VALID_TYPE_PRIX]
        if invalid:
            raise serializers.ValidationError(
                _("Valeur(s) invalide(s) : %(values)s") % {"values": ", ".join(invalid)}
            )
        return value

    def validate_numero_contrat(self, value: str) -> str:
        """Ensure numero_contrat is unique within the same company + contract_category."""
        company = self.initial_data.get("company") or (
            self.instance.company if self.instance else None
        )
        contract_category = self.initial_data.get("contract_category") or (
            self.instance.contract_category if self.instance else None
        )
        qs = Contract.objects.filter(numero_contrat=value)
        if company:
            qs = qs.filter(company=company)
        if contract_category:
            qs = qs.filter(contract_category=contract_category)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                _("Un contrat avec ce numéro existe déjà.")
            )
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        company = attrs.get(
            "company",
            getattr(
                self.instance, "company", Contract._meta.get_field("company").default
            ),
        )
        contract_category = attrs.get(
            "contract_category",
            getattr(
                self.instance,
                "contract_category",
                Contract._meta.get_field("contract_category").default,
            ),
        )
        errors = {}

        if company == "casa_di_lusso" and contract_category != "sous_traitance":
            tranches = attrs.get("tranches", getattr(self.instance, "tranches", []))
            if not _has_valid_echeancier_total(tranches):
                errors["tranches"] = [ECHEANCIER_TOTAL_ERROR]

        if company == "casa_di_lusso" and contract_category == "sous_traitance":
            st_tranches = attrs.get(
                "st_tranches", getattr(self.instance, "st_tranches", [])
            )
            if not _has_valid_echeancier_total(st_tranches):
                errors["st_tranches"] = [ECHEANCIER_TOTAL_ERROR]

        acompte = attrs.get("acompte", getattr(self.instance, "acompte", None))
        tranche2 = attrs.get("tranche2", getattr(self.instance, "tranche2", None))
        a = acompte or 0
        t = tranche2 or 0
        if a + t > 100:
            errors["acompte"] = [
                _("La somme de l'acompte et de la tranche 2 ne peut pas dépasser 100%.")
            ]
            errors["tranche2"] = [
                _("La somme de l'acompte et de la tranche 2 ne peut pas dépasser 100%.")
            ]

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    class Meta:
        model = Contract
        fields = [
            "id",
            "numero_contrat",
            "company",
            "company_display",
            "contract_category",
            "contract_category_display",
            "client_name",
            "client_nom",
            "client_cin",
            "client_qualite",
            "client_adresse",
            "client_tel",
            "client_email",
            "ville_signature",
            "date_contrat",
            "statut",
            # Project
            "adresse_travaux",
            "type_bien",
            "surface",
            "services",
            "description_travaux",
            "date_debut",
            "duree_estimee",
            "conditions_acces",
            # Financial
            "montant_ht",
            "devise",
            "tva",
            "montant_tva",
            "montant_ttc",
            "tranches",
            "mode_paiement_texte",
            "rib",
            "delai_retard",
            "penalite_retard",
            "penalite_retard_unite",
            "frais_redemarrage",
            # Clauses
            "garantie",
            "delai_reserves",
            "tribunal",
            "clauses_actives",
            "clause_spec",
            "exclusions",
            # Options
            "type_contrat",
            "type_contrat_display",
            "responsable_projet",
            "architecte",
            "confidentialite",
            "annexes",
            # Blueline Works specific
            "client_ville",
            "client_cp",
            "chantier_ville",
            "chantier_etage",
            "prestations",
            "fournitures",
            "materiaux_detail",
            "eau_electricite",
            "garantie_nb",
            "garantie_unite",
            "garantie_type",
            "exclusions_garantie",
            "acompte",
            "tranche2",
            "solde",
            "clause_resiliation",
            "notes",
            # Sous-Traitance specific
            "st_projet",
            "st_projet_detail",
            "st_name",
            "st_forme",
            "st_capital",
            "st_rc",
            "st_ice",
            "st_if",
            "st_cnss",
            "st_addr",
            "st_rep",
            "st_cin",
            "st_qualite",
            "st_tel",
            "st_email",
            "st_rib",
            "st_banque",
            "st_lot_type",
            "st_lot_description",
            "st_type_prix",
            "st_retenue_garantie",
            "st_avance",
            "st_penalite_taux",
            "st_plafond_penalite",
            "st_delai_paiement",
            "st_tranches",
            "st_delai_val",
            "st_delai_unit",
            "st_garantie_mois",
            "st_delai_reserves",
            "st_delai_med",
            "st_clauses_actives",
            "st_observations",
            # Meta
            "created_by_user",
            "created_by_user_id",
            "created_by_user_name",
            "date_created",
            "date_updated",
        ]
        read_only_fields = [
            "id",
            "client_name",
            "company_display",
            "contract_category_display",
            "created_by_user",
            "created_by_user_name",
            "created_by_user_id",
            "montant_tva",
            "montant_ttc",
            "solde",
            "statut",
            "type_contrat_display",
            "st_projet_detail",
            "date_created",
            "date_updated",
        ]
