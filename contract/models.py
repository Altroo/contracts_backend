from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from account.models import CustomUser
from core.constants import (
    COMPANY_CHOICES,
    CONTRACT_CATEGORY_CHOICES,
    CURRENCY_CHOICES,
    GARANTIE_CHOICES,
    MODE_PAIEMENT_TEXTE_CHOICES,
    STATUT_CHOICES,
    TRIBUNAL_CHOICES,
    CLIENT_QUALITE_CHOICES,
    CONTRACT_TYPE_CHOICES,
    CONFIDENTIALITE_CHOICES,
    TYPE_BIEN_CHOICES,
    FOURNITURES_CHOICES,
    EAU_ELECTRICITE_CHOICES,
    GARANTIE_UNITE_CHOICES,
    GARANTIE_TYPE_CHOICES,
    CLAUSE_RESILIATION_CHOICES,
    ST_PROJET_TYPE_CHOICES,
    ST_FORME_JURIDIQUE_CHOICES,
    ST_DELAI_UNIT_CHOICES,
)


class Project(models.Model):
    """Projet de construction, shared across sous-traitance contracts."""

    company = models.CharField(
        max_length=50,
        choices=COMPANY_CHOICES,
        default="casa_di_lusso",
        verbose_name=_("Société"),
        db_index=True,
    )
    name = models.CharField(max_length=300, verbose_name=_("Nom du projet"))
    type = models.CharField(
        max_length=50,
        choices=ST_PROJET_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Type de projet"),
    )
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    adresse = models.TextField(blank=True, null=True, verbose_name=_("Adresse du projet"))
    maitre_ouvrage = models.CharField(
        max_length=300, blank=True, null=True, verbose_name=_("Maître d'ouvrage")
    )
    permis = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("N° permis de construire"),
    )
    is_predefined = models.BooleanField(
        default=False,
        verbose_name=_("Prédéfini"),
        help_text=_("Prédéfini par l'admin, non supprimable par les utilisateurs."),
    )
    created_by_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_created",
        verbose_name=_("Créé par"),
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Projet")
        verbose_name_plural = _("Projets")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Contract(models.Model):
    """Contract model for construction / design contracts (multi-company)."""

    STATUT_CHOICES = STATUT_CHOICES

    company = models.CharField(
        max_length=50,
        choices=COMPANY_CHOICES,
        default="casa_di_lusso",
        verbose_name=_("Société"),
        db_index=True,
    )
    contract_category = models.CharField(
        max_length=30,
        choices=CONTRACT_CATEGORY_CHOICES,
        default="standard",
        verbose_name=_("Catégorie de contrat"),
        db_index=True,
    )

    numero_contrat = models.CharField(
        max_length=30,
        verbose_name=_("Référence contrat"),
        help_text=_("Format ex: 0001/26"),
    )
    date_contrat = models.DateField(
        verbose_name=_("Date du contrat"),
        db_index=True,
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="Brouillon",
        verbose_name=_("Statut"),
        db_index=True,
    )

    client_nom = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("Nom & Prénom")
    )
    client_cin = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_("CIN / ICE / Passeport")
    )
    client_qualite = models.CharField(
        max_length=50,
        choices=CLIENT_QUALITE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Qualité du client"),
    )
    client_adresse = models.TextField(
        blank=True, null=True, verbose_name=_("Adresse complète")
    )
    client_tel = models.CharField(
        max_length=30, blank=True, null=True, verbose_name=_("Téléphone")
    )
    client_email = models.EmailField(blank=True, null=True, verbose_name=_("Email"))
    ville_signature = models.CharField(
        max_length=100,
        default="Tanger",
        verbose_name=_("Ville de signature"),
    )

    adresse_travaux = models.TextField(
        blank=True, null=True, verbose_name=_("Adresse des travaux")
    )
    type_bien = models.CharField(
        max_length=50,
        choices=TYPE_BIEN_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Type de bien"),
    )
    surface = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Surface (m²)"),
    )
    services = models.JSONField(
        default=list, blank=True, verbose_name=_("Services sélectionnés")
    )
    description_travaux = models.TextField(
        blank=True, null=True, verbose_name=_("Description des travaux")
    )
    date_debut = models.DateField(
        null=True, blank=True, verbose_name=_("Date de début prévue")
    )
    duree_estimee = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Durée estimée"),
    )
    conditions_acces = models.TextField(
        blank=True, null=True, verbose_name=_("Conditions d'accès")
    )

    montant_ht = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name=_("Montant total HT"),
    )
    devise = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="MAD",
        verbose_name=_("Devise"),
    )
    tva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20,
        verbose_name=_("TVA (%)"),
    )
    tranches = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Echéancier de paiement"),
        help_text=_("Liste de {label, pourcentage}"),
    )
    mode_paiement_texte = models.CharField(
        max_length=100,
        choices=MODE_PAIEMENT_TEXTE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Mode de paiement"),
    )
    rib = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("RIB / Coordonnées bancaires"),
    )
    delai_retard = models.IntegerField(
        default=5, verbose_name=_("Délai retard toléré (jours)")
    )
    penalite_retard = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Pénalité retard (MAD/j)"),
    )
    frais_redemarrage = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Frais de redémarrage (MAD)"),
    )

    garantie = models.CharField(
        max_length=50,
        choices=GARANTIE_CHOICES,
        default="1 an",
        verbose_name=_("Durée de garantie"),
    )
    delai_reserves = models.IntegerField(
        default=7, verbose_name=_("Délai réserves (j ouvrés)")
    )
    tribunal = models.CharField(
        max_length=50,
        choices=TRIBUNAL_CHOICES,
        default="Tanger",
        verbose_name=_("Tribunal compétent"),
    )
    clauses_actives = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Clauses actives"),
    )
    clause_spec = models.TextField(
        blank=True, null=True, verbose_name=_("Clauses spécifiques additionnelles")
    )
    exclusions = models.TextField(
        blank=True, null=True, verbose_name=_("Exclusions explicites")
    )

    type_contrat = models.CharField(
        max_length=50,
        choices=CONTRACT_TYPE_CHOICES,
        default="travaux_finition",
        verbose_name=_("Type de contrat"),
    )
    responsable_projet = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Responsable de projet CASA DI LUSSO"),
    )
    architecte = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Architecte / Designer associé"),
    )
    confidentialite = models.CharField(
        max_length=30,
        choices=CONFIDENTIALITE_CHOICES,
        default="CONFIDENTIEL",
        verbose_name=_("Note de confidentialité"),
    )
    annexes = models.TextField(blank=True, null=True, verbose_name=_("Annexes jointes"))

    # ── Blueline Works specific fields ───────────────────────────────────────
    client_ville = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Ville du client"),
    )
    client_cp = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name=_("Code postal client"),
    )
    chantier_ville = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Ville du chantier"),
    )
    chantier_etage = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Étage / Appartement"),
    )
    prestations = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Prestations"),
        help_text=_("Liste de {nom, desc, qte, unite, pu}"),
    )
    fournitures = models.CharField(
        max_length=50,
        choices=FOURNITURES_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Fournitures incluses"),
    )
    materiaux_detail = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Matériaux à fournir par le client"),
    )
    eau_electricite = models.CharField(
        max_length=50,
        choices=EAU_ELECTRICITE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Eau & Électricité sur chantier"),
    )
    garantie_nb = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Durée de garantie (valeur)"),
    )
    garantie_unite = models.CharField(
        max_length=10,
        choices=GARANTIE_UNITE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Unité de garantie"),
    )
    garantie_type = models.CharField(
        max_length=50,
        choices=GARANTIE_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Type de garantie"),
    )
    exclusions_garantie = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Exclusions de garantie"),
    )
    acompte = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Acompte (%)"),
    )
    tranche2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("2ème tranche (%)"),
    )
    clause_resiliation = models.CharField(
        max_length=50,
        choices=CLAUSE_RESILIATION_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Clause de résiliation"),
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Notes & Observations"))

    # ── Sous-Traitance specific fields ───────────────────────────────────────
    st_projet = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts",
        verbose_name=_("Projet"),
    )
    # Sous-traitant identity
    st_name = models.CharField(
        max_length=300, blank=True, null=True, verbose_name=_("Raison sociale ST")
    )
    st_forme = models.CharField(
        max_length=50,
        choices=ST_FORME_JURIDIQUE_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Forme juridique ST"),
    )
    st_capital = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Capital social ST"),
    )
    st_rc = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("RC ST")
    )
    st_ice = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("ICE ST")
    )
    st_if = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Identifiant fiscal ST"),
    )
    st_cnss = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("CNSS ST")
    )
    st_addr = models.TextField(blank=True, null=True, verbose_name=_("Adresse siège ST"))
    st_rep = models.CharField(
        max_length=300, blank=True, null=True, verbose_name=_("Représentant ST")
    )
    st_cin = models.CharField(
        max_length=50, blank=True, null=True, verbose_name=_("CIN représentant ST")
    )
    st_qualite = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Qualité représentant ST"),
    )
    st_tel = models.CharField(
        max_length=30, blank=True, null=True, verbose_name=_("Téléphone ST")
    )
    st_email = models.EmailField(blank=True, null=True, verbose_name=_("Email ST"))
    st_rib = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("RIB ST")
    )
    st_banque = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=_("Banque ST")
    )
    # Lot / Travaux
    st_lot_type = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Type(s) de lot"),
    )
    st_lot_description = models.TextField(
        blank=True, null=True, verbose_name=_("Description du lot")
    )
    st_type_prix = models.JSONField(
        default=list,
        blank=True,
        null=True,
        verbose_name=_("Type(s) de prix"),
    )
    # Financial
    st_retenue_garantie = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Retenue de garantie (%)"),
    )
    st_avance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Avance forfaitaire (%)"),
    )
    st_penalite_taux = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Pénalité retard (MAD/jour)"),
    )
    st_plafond_penalite = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Plafond pénalité (%)"),
    )
    st_delai_paiement = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Délai de paiement (jours)"),
    )
    st_tranches = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Tranches paiement ST"),
        help_text=_("{label, pourcentage}"),
    )
    # Delays
    st_delai_val = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Délai d'exécution (valeur)"),
    )
    st_delai_unit = models.CharField(
        max_length=20,
        choices=ST_DELAI_UNIT_CHOICES,
        blank=True,
        null=True,
        verbose_name=_("Unité délai d'exécution"),
    )
    st_garantie_mois = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Garantie décennale (mois)"),
    )
    st_delai_reserves = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Délai levée réserves (jours)"),
    )
    st_delai_med = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Délai mise en demeure (jours)"),
    )
    # Options
    st_clauses_actives = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Clauses actives ST"),
    )
    st_observations = models.TextField(
        blank=True, null=True, verbose_name=_("Observations ST")
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts_created",
        verbose_name=_("Créé par"),
    )
    history = HistoricalRecords(verbose_name=_("Historique Contrat"))

    class Meta:
        verbose_name = _("Contrat")
        verbose_name_plural = _("Contrats")
        ordering = ("-date_created",)
        unique_together = [("company", "contract_category", "numero_contrat")]
        indexes = [
            models.Index(fields=["date_contrat"]),
            models.Index(fields=["statut"]),
        ]

    def __str__(self) -> str:
        return self.numero_contrat

    @property
    def montant_tva(self) -> float:
        return float(self.montant_ht) * float(self.tva) / 100

    @property
    def montant_ttc(self) -> float:
        return float(self.montant_ht) + self.montant_tva

    @property
    def solde(self) -> float:
        """Compute remaining payment percentage: 100 - acompte - tranche2."""
        return 100 - float(self.acompte or 0) - float(self.tranche2 or 0)
