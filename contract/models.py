from django.db import models
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
    ST_LOT_TYPE_CHOICES,
    ST_PROJET_TYPE_CHOICES,
    ST_FORME_JURIDIQUE_CHOICES,
    ST_TYPE_PRIX_CHOICES,
    ST_DELAI_UNIT_CHOICES,
)


class Project(models.Model):
    """Projet de construction, shared across sous-traitance contracts."""

    company = models.CharField(
        max_length=50,
        choices=COMPANY_CHOICES,
        default="casa_di_lusso",
        verbose_name="Société",
        db_index=True,
    )
    name = models.CharField(max_length=300, verbose_name="Nom du projet")
    type = models.CharField(
        max_length=50,
        choices=ST_PROJET_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Type de projet",
    )
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    adresse = models.TextField(blank=True, null=True, verbose_name="Adresse du projet")
    maitre_ouvrage = models.CharField(
        max_length=300, blank=True, null=True, verbose_name="Maître d'ouvrage"
    )
    permis = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="N° permis de construire",
    )
    is_predefined = models.BooleanField(
        default=False,
        verbose_name="Prédéfini",
        help_text="Prédéfini par l'admin, non supprimable par les utilisateurs.",
    )
    created_by_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects_created",
        verbose_name="Créé par",
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Contract(models.Model):
    """Contract model for construction / design contracts (multi-company)."""

    STATUT_CHOICES = STATUT_CHOICES

    # ── Company ──────────────────────────────────────────────────────────────
    company = models.CharField(
        max_length=50,
        choices=COMPANY_CHOICES,
        default="casa_di_lusso",
        verbose_name="Société",
        db_index=True,
    )
    contract_category = models.CharField(
        max_length=30,
        choices=CONTRACT_CATEGORY_CHOICES,
        default="standard",
        verbose_name="Catégorie de contrat",
        db_index=True,
    )

    numero_contrat = models.CharField(
        max_length=30,
        verbose_name="Référence contrat",
        help_text="Format ex: 0001/26",
    )
    date_contrat = models.DateField(
        verbose_name="Date du contrat",
        db_index=True,
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="Brouillon",
        verbose_name="Statut",
        db_index=True,
    )

    client_nom = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Nom & Prénom"
    )
    client_cin = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="CIN / ICE / Passeport"
    )
    client_qualite = models.CharField(
        max_length=50,
        choices=CLIENT_QUALITE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Qualité du client",
    )
    client_adresse = models.TextField(
        blank=True, null=True, verbose_name="Adresse complète"
    )
    client_tel = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Téléphone"
    )
    client_email = models.EmailField(blank=True, null=True, verbose_name="Email")
    ville_signature = models.CharField(
        max_length=100,
        default="Tanger",
        verbose_name="Ville de signature",
    )

    adresse_travaux = models.TextField(
        blank=True, null=True, verbose_name="Adresse des travaux"
    )
    type_bien = models.CharField(
        max_length=50,
        choices=TYPE_BIEN_CHOICES,
        blank=True,
        null=True,
        verbose_name="Type de bien",
    )
    surface = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Surface (m²)",
    )
    services = models.JSONField(
        default=list, blank=True, verbose_name="Services sélectionnés"
    )
    description_travaux = models.TextField(
        blank=True, null=True, verbose_name="Description des travaux"
    )
    date_debut = models.DateField(
        null=True, blank=True, verbose_name="Date de début prévue"
    )
    duree_estimee = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Durée estimée",
    )
    conditions_acces = models.TextField(
        blank=True, null=True, verbose_name="Conditions d'accès"
    )

    montant_ht = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="Montant total HT",
    )
    devise = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default="MAD",
        verbose_name="Devise",
    )
    tva = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20,
        verbose_name="TVA (%)",
    )
    tranches = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Échéancier de paiement",
        help_text="Liste de {label, pourcentage}",
    )
    mode_paiement_texte = models.CharField(
        max_length=100,
        choices=MODE_PAIEMENT_TEXTE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Mode de paiement",
    )
    rib = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="RIB / Coordonnées bancaires",
    )
    delai_retard = models.IntegerField(
        default=5, verbose_name="Délai retard toléré (jours)"
    )
    penalite_retard = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.5,
        verbose_name="Pénalité retard (%/j)",
    )
    frais_redemarrage = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Frais de redémarrage (MAD)",
    )

    garantie = models.CharField(
        max_length=50,
        choices=GARANTIE_CHOICES,
        default="1 an",
        verbose_name="Durée de garantie",
    )
    delai_reserves = models.IntegerField(
        default=7, verbose_name="Délai réserves (j ouvrés)"
    )
    tribunal = models.CharField(
        max_length=50,
        choices=TRIBUNAL_CHOICES,
        default="Tanger",
        verbose_name="Tribunal compétent",
    )
    clauses_actives = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Clauses actives",
    )
    clause_spec = models.TextField(
        blank=True, null=True, verbose_name="Clauses spécifiques additionnelles"
    )
    exclusions = models.TextField(
        blank=True, null=True, verbose_name="Exclusions explicites"
    )

    type_contrat = models.CharField(
        max_length=50,
        choices=CONTRACT_TYPE_CHOICES,
        default="travaux_finition",
        verbose_name="Type de contrat",
    )
    responsable_projet = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Responsable de projet CASA DI LUSSO",
    )
    architecte = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Architecte / Designer associé",
    )
    confidentialite = models.CharField(
        max_length=30,
        choices=CONFIDENTIALITE_CHOICES,
        default="CONFIDENTIEL",
        verbose_name="Note de confidentialité",
    )
    version_document = models.CharField(
        max_length=50,
        default="v1.0 – Définitif",
        verbose_name="Version du document",
    )
    annexes = models.TextField(blank=True, null=True, verbose_name="Annexes jointes")

    # ── Blueline Works specific fields ───────────────────────────────────────
    client_ville = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ville du client",
    )
    client_cp = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Code postal client",
    )
    chantier_ville = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ville du chantier",
    )
    chantier_etage = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Étage / Appartement",
    )
    prestations = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Prestations",
        help_text="Liste de {nom, desc, qte, unite, pu}",
    )
    fournitures = models.CharField(
        max_length=50,
        choices=FOURNITURES_CHOICES,
        blank=True,
        null=True,
        verbose_name="Fournitures incluses",
    )
    materiaux_detail = models.TextField(
        blank=True,
        null=True,
        verbose_name="Matériaux à fournir par le client",
    )
    eau_electricite = models.CharField(
        max_length=50,
        choices=EAU_ELECTRICITE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Eau & Électricité sur chantier",
    )
    garantie_nb = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Durée de garantie (valeur)",
    )
    garantie_unite = models.CharField(
        max_length=10,
        choices=GARANTIE_UNITE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Unité de garantie",
    )
    garantie_type = models.CharField(
        max_length=50,
        choices=GARANTIE_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Type de garantie",
    )
    exclusions_garantie = models.TextField(
        blank=True,
        null=True,
        verbose_name="Exclusions de garantie",
    )
    acompte = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Acompte (%)",
    )
    tranche2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="2ème tranche (%)",
    )
    clause_resiliation = models.CharField(
        max_length=50,
        choices=CLAUSE_RESILIATION_CHOICES,
        blank=True,
        null=True,
        verbose_name="Clause de résiliation",
    )
    notes = models.TextField(blank=True, null=True, verbose_name="Notes & Observations")

    # ── Sous-Traitance specific fields ───────────────────────────────────────
    st_projet = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts",
        verbose_name="Projet",
    )
    # Sous-traitant identity
    st_name = models.CharField(
        max_length=300, blank=True, null=True, verbose_name="Raison sociale ST"
    )
    st_forme = models.CharField(
        max_length=50,
        choices=ST_FORME_JURIDIQUE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Forme juridique ST",
    )
    st_capital = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Capital social ST",
    )
    st_rc = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="RC ST"
    )
    st_ice = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="ICE ST"
    )
    st_if = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Identifiant fiscal ST",
    )
    st_cnss = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="CNSS ST"
    )
    st_addr = models.TextField(blank=True, null=True, verbose_name="Adresse siège ST")
    st_rep = models.CharField(
        max_length=300, blank=True, null=True, verbose_name="Représentant ST"
    )
    st_cin = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="CIN représentant ST"
    )
    st_qualite = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Qualité représentant ST",
    )
    st_tel = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="Téléphone ST"
    )
    st_email = models.EmailField(blank=True, null=True, verbose_name="Email ST")
    st_rib = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="RIB ST"
    )
    st_banque = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="Banque ST"
    )
    # Lot / Travaux
    st_lot_type = models.CharField(
        max_length=50,
        choices=ST_LOT_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Type de lot",
    )
    st_lot_description = models.TextField(
        blank=True, null=True, verbose_name="Description du lot"
    )
    st_type_prix = models.CharField(
        max_length=30,
        choices=ST_TYPE_PRIX_CHOICES,
        blank=True,
        null=True,
        verbose_name="Type de prix",
    )
    # Financial
    st_retenue_garantie = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Retenue de garantie (%)",
    )
    st_avance = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Avance forfaitaire (%)",
    )
    st_penalite_taux = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Pénalité retard (‰/jour)",
    )
    st_plafond_penalite = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Plafond pénalité (%)",
    )
    st_delai_paiement = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Délai de paiement (jours)",
    )
    st_tranches = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tranches paiement ST",
        help_text="[{label, pourcentage}]",
    )
    # Delays
    st_delai_val = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Délai d'exécution (valeur)",
    )
    st_delai_unit = models.CharField(
        max_length=20,
        choices=ST_DELAI_UNIT_CHOICES,
        blank=True,
        null=True,
        verbose_name="Unité délai d'exécution",
    )
    st_garantie_mois = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Garantie décennale (mois)",
    )
    st_delai_reserves = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Délai levée réserves (jours)",
    )
    st_delai_med = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Délai mise en demeure (jours)",
    )
    # Options
    st_clauses_actives = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Clauses actives ST",
    )
    st_observations = models.TextField(
        blank=True, null=True, verbose_name="Observations ST"
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    created_by_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contracts_created",
        verbose_name="Créé par",
    )
    history = HistoricalRecords(verbose_name="Historique Contrat")

    class Meta:
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"
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
