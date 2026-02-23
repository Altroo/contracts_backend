from django.db import models
from simple_history.models import HistoricalRecords

from account.models import CustomUser
from core.constants import CURRENCY_CHOICES


CONTRACT_TYPE_CHOICES = [
    ("travaux_finition", "Travaux de Finition"),
    ("travaux_gros_oeuvre", "Travaux Gros Œuvre"),
    ("design_interieur", "Design Intérieur"),
    ("cle_en_main", "Clé en Main"),
    ("ameublement", "Ameublement"),
    ("maintenance", "Maintenance"),
    ("suivi_chantier", "Suivi Chantier"),
]

TYPE_BIEN_CHOICES = [
    ("appartement", "Appartement"),
    ("villa", "Villa"),
    ("riad_maison_traditionnelle", "Riad / Maison Traditionnelle"),
    ("bureau_local_commercial", "Bureau / Local Commercial"),
    ("hotel_riad_hotelier", "Hôtel / Riad Hôtelier"),
    ("autre", "Autre"),
]

CLIENT_QUALITE_CHOICES = [
    ("particulier", "Particulier"),
    ("entreprise_societe", "Entreprise / Société"),
    ("investisseur_immobilier", "Investisseur Immobilier"),
    ("administration_institution", "Administration / Institution"),
]

GARANTIE_CHOICES = [
    ("6 mois", "6 mois"),
    ("1 an", "1 an"),
    ("2 ans", "2 ans"),
    ("3 ans", "3 ans"),
    ("sans_garantie", "Sans garantie contractuelle"),
]

TRIBUNAL_CHOICES = [
    ("Tanger", "Tanger"),
    ("Casablanca", "Casablanca"),
    ("Rabat", "Rabat"),
    ("Marrakech", "Marrakech"),
    ("Fès", "Fès"),
    ("Agadir", "Agadir"),
]

CONFIDENTIALITE_CHOICES = [
    ("CONFIDENTIEL", "CONFIDENTIEL"),
    ("USAGE INTERNE", "USAGE INTERNE"),
    ("STANDARD", "STANDARD"),
]

STATUT_CHOICES = [
    ("Brouillon", "Brouillon"),
    ("Envoyé", "Envoyé"),
    ("Signé", "Signé"),
    ("En cours", "En cours"),
    ("Terminé", "Terminé"),
    ("Annulé", "Annulé"),
    ("Expiré", "Expiré"),
]

MODE_PAIEMENT_TEXTE_CHOICES = [
    ("Virement Bancaire", "Virement Bancaire"),
    ("Chèque Certifié", "Chèque Certifié"),
    ("Espèces", "Espèces"),
    ("Paiement Mixte", "Paiement Mixte"),
]


class Contract(models.Model):
    """Contract model for Casa di Lusso construction / design contracts."""

    STATUT_CHOICES = STATUT_CHOICES

    # ── Reference & Date ──────────────────────────────────────────────────
    numero_contrat = models.CharField(
        max_length=30,
        unique=True,
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

    # ── Client (denormalised fields, no FK) ───────────────────────────────
    client_nom = models.CharField(max_length=200, blank=True, null=True, verbose_name="Nom & Prénom")
    client_cin = models.CharField(max_length=50, blank=True, null=True, verbose_name="CIN / ICE / Passeport")
    client_qualite = models.CharField(
        max_length=50,
        choices=CLIENT_QUALITE_CHOICES,
        blank=True,
        null=True,
        verbose_name="Qualité du client",
    )
    client_adresse = models.TextField(blank=True, null=True, verbose_name="Adresse complète")
    client_tel = models.CharField(max_length=30, blank=True, null=True, verbose_name="Téléphone")
    client_email = models.EmailField(blank=True, null=True, verbose_name="Email")
    ville_signature = models.CharField(
        max_length=100,
        default="Tanger",
        verbose_name="Ville de signature",
    )

    # ── Project & Services ────────────────────────────────────────────────
    adresse_travaux = models.TextField(blank=True, null=True, verbose_name="Adresse des travaux")
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
    services = models.JSONField(default=list, blank=True, verbose_name="Services sélectionnés")
    description_travaux = models.TextField(blank=True, null=True, verbose_name="Description des travaux")
    date_debut = models.DateField(null=True, blank=True, verbose_name="Date de début prévue")
    duree_estimee = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Durée estimée",
    )
    conditions_acces = models.TextField(blank=True, null=True, verbose_name="Conditions d'accès")

    # ── Financial ─────────────────────────────────────────────────────────
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
    rib = models.CharField(max_length=200, blank=True, null=True, verbose_name="RIB / Coordonnées bancaires")
    delai_retard = models.IntegerField(default=5, verbose_name="Délai retard toléré (jours)")
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

    # ── Legal Clauses ─────────────────────────────────────────────────────
    garantie = models.CharField(
        max_length=50,
        choices=GARANTIE_CHOICES,
        default="1 an",
        verbose_name="Durée de garantie",
    )
    delai_reserves = models.IntegerField(default=7, verbose_name="Délai réserves (j ouvrés)")
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
    clause_spec = models.TextField(blank=True, null=True, verbose_name="Clauses spécifiques additionnelles")
    exclusions = models.TextField(blank=True, null=True, verbose_name="Exclusions explicites")

    # ── Options & Presentation ────────────────────────────────────────────
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

    # ── Meta ──────────────────────────────────────────────────────────────
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
