from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Contract


class ContractAdmin(SimpleHistoryAdmin):
    list_display = (
        "numero_contrat",
        "company",
        "client_nom",
        "date_contrat",
        "type_contrat",
        "statut",
        "montant_ht",
        "devise",
        "confidentialite",
        "created_by_user",
        "date_created",
    )
    list_filter = ("company", "statut", "type_contrat", "devise", "confidentialite")
    search_fields = ("numero_contrat", "client_nom", "client_email", "adresse_travaux")
    ordering = ("-date_created",)
    readonly_fields = ("date_created", "date_updated", "created_by_user")
    fieldsets = (
        (
            "Référence & Statut",
            {
                "fields": (
                    "company",
                    "numero_contrat",
                    "date_contrat",
                    "statut",
                    "confidentialite",
                    "version_document",
                )
            },
        ),
        (
            "Client",
            {
                "fields": (
                    "client_nom",
                    "client_cin",
                    "client_qualite",
                    "client_adresse",
                    "client_tel",
                    "client_email",
                    "ville_signature",
                )
            },
        ),
        (
            "Projet & Services",
            {
                "fields": (
                    "adresse_travaux",
                    "type_bien",
                    "surface",
                    "services",
                    "description_travaux",
                    "date_debut",
                    "duree_estimee",
                    "conditions_acces",
                )
            },
        ),
        (
            "Conditions Financières",
            {
                "fields": (
                    "montant_ht",
                    "devise",
                    "tva",
                    "tranches",
                    "mode_paiement_texte",
                    "rib",
                    "delai_retard",
                    "penalite_retard",
                    "frais_redemarrage",
                )
            },
        ),
        (
            "Clauses Juridiques",
            {
                "fields": (
                    "garantie",
                    "delai_reserves",
                    "tribunal",
                    "clauses_actives",
                    "clause_spec",
                    "exclusions",
                )
            },
        ),
        (
            "Options",
            {
                "fields": (
                    "type_contrat",
                    "responsable_projet",
                    "architecte",
                    "annexes",
                )
            },
        ),
        (
            "Blueline Works",
            {
                "classes": ("collapse",),
                "fields": (
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
                    "clause_resiliation",
                    "notes",
                ),
            },
        ),
        (
            "Métadonnées",
            {
                "fields": ("created_by_user", "date_created", "date_updated"),
            },
        ),
    )


admin.site.register(Contract, ContractAdmin)
