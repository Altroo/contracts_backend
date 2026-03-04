from rest_framework import serializers

from .models import Contract


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
    solde = serializers.SerializerMethodField(read_only=True)

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

    def validate_numero_contrat(self, value: str) -> str:
        """Ensure numero_contrat is unique within the same company."""
        company = self.initial_data.get("company") or (
            self.instance.company if self.instance else None
        )
        qs = Contract.objects.filter(numero_contrat=value)
        if company:
            qs = qs.filter(company=company)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Un contrat avec ce numéro existe déjà.")
        return value

    class Meta:
        model = Contract
        fields = [
            "id",
            "numero_contrat",
            "company",
            "company_display",
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
            "version_document",
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
            "created_by_user_name",
            "created_by_user_id",
            "montant_tva",
            "montant_ttc",
            "solde",
            "type_contrat_display",
            "date_created",
            "date_updated",
        ]
