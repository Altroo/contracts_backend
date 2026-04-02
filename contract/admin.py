from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from simple_history.admin import SimpleHistoryAdmin

from .models import Contract, Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "company",
        "type",
        "maitre_ouvrage",
        "is_predefined",
        "date_created",
    )
    list_filter = ("company", "type", "is_predefined")
    search_fields = ("name", "maitre_ouvrage", "adresse", "permis")
    ordering = ("name",)
    readonly_fields = ("date_created", "date_updated", "created_by_user")


class ContractAdmin(SimpleHistoryAdmin):
    list_display = (
        "numero_contrat",
        "company",
        "contract_category",
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
    list_filter = (
        "company",
        "contract_category",
        "statut",
        "type_contrat",
        "devise",
        "confidentialite",
    )
    search_fields = (
        "numero_contrat",
        "client_nom",
        "client_email",
        "adresse_travaux",
        "st_name",
        "st_rep",
    )
    ordering = ("-date_created",)
    readonly_fields = ("date_created", "date_updated", "created_by_user")
    fieldsets = (
        (
            _("Référence & Statut"),
            {
                "fields": (
                    "company",
                    "contract_category",
                    "numero_contrat",
                    "date_contrat",
                    "statut",
                    "confidentialite",
                )
            },
        ),
        (
            _("Client"),
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
            _("Projet & Services"),
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
            _("Conditions Financières"),
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
            _("Clauses Juridiques"),
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
            _("Options"),
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
            _("Blueline Works"),
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
            _("Sous-Traitance"),
            {
                "classes": ("collapse",),
                "fields": (
                    "st_projet",
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
                ),
            },
        ),
        (
            _("Métadonnées"),
            {
                "fields": ("created_by_user", "date_created", "date_updated"),
            },
        ),
    )


admin.site.register(Project, ProjectAdmin)
admin.site.register(Contract, ContractAdmin)
