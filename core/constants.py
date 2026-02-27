"""
Shared constants used across multiple apps.
"""

CURRENCY_CHOICES = [
    ("MAD", "MAD – Dirham Marocain"),
    ("EUR", "EUR – Euro"),
    ("USD", "USD – Dollar Américain"),
]

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
