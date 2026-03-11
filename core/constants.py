"""
Shared constants used across multiple apps.
"""

COMPANY_CHOICES = [
    ("casa_di_lusso", "Casa di Lusso"),
    ("blueline_works", "Blueline Works"),
]

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
    ("duplex", "Duplex"),
    ("residence", "Résidence"),
    ("hotel", "Hôtel"),
    ("riad_maison_traditionnelle", "Riad / Maison Traditionnelle"),
    ("bureau_local_commercial", "Bureau / Local Commercial"),
    ("commerce_local", "Commerce / Local"),
    ("hotel_riad_hotelier", "Hôtel / Riad Hôtelier"),
    ("immeuble", "Immeuble"),
    ("autre", "Autre"),
]

CLIENT_QUALITE_CHOICES = [
    ("particulier", "Particulier"),
    ("entreprise_societe", "Entreprise / Société"),
    ("investisseur_immobilier", "Investisseur Immobilier"),
    ("administration_institution", "Administration / Institution"),
]


GARANTIE_CHOICES = [
    ("1 mois", "1 mois"),
    ("3 mois", "3 mois"),
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
    ("Mobile Money", "Mobile Money"),
    ("Virement ou Chèque", "Virement ou Chèque"),
]

# ── Blueline Works specific choices ────────────────────────────────────────

FOURNITURES_CHOICES = [
    ("non_incluses", "Non incluses (fournies par le client)"),
    ("incluses", "Incluses dans le contrat"),
    ("partielles", "Partiellement incluses"),
]

EAU_ELECTRICITE_CHOICES = [
    ("client", "À la charge du client"),
    ("entreprise", "À la charge de l'entreprise"),
    ("partage", "Partagé"),
    ("selon_cas", "Selon le cas"),
]

GARANTIE_UNITE_CHOICES = [
    ("mois", "Mois"),
    ("ans", "Ans"),
]

GARANTIE_TYPE_CHOICES = [
    ("defauts", "Garantie des défauts"),
    ("bonne_fin", "Garantie de bonne fin"),
    ("decennale", "Garantie décennale"),
    ("aucune", "Aucune garantie"),
]

CLAUSE_RESILIATION_CHOICES = [
    ("30j", "Préavis de 30 jours"),
    ("15j", "Préavis de 15 jours"),
    ("mutuel", "D'un commun accord"),
    ("aucune", "Aucune clause"),
]

PRESTATION_NOM_CHOICES = [
    ("pose_carrelage", "Pose de carrelage"),
    ("pose_marbre", "Pose de marbre"),
    ("plan_travail_cuisine", "Plan de travail cuisine"),
    ("revetement_mural_faience", "Revêtement mural faïence"),
    ("finitions_peinture", "Finitions peinture"),
    ("pose_parquet", "Pose de parquet"),
    ("enduit_crepi", "Enduit & crépi"),
    ("joints_silicone", "Joints & silicone"),
    ("depose_demolition", "Dépose & démolition"),
    ("preparation_surfaces", "Préparation des surfaces"),
    ("seuils_plinthes", "Seuils & plinthes"),
    ("douche_italienne", "Douche à l'italienne"),
    ("escalier_marbre", "Escalier marbre"),
    ("terrasse_exterieure", "Terrasse extérieure"),
    ("main_oeuvre", "Main d'œuvre qualifiée"),
    ("transport_deplacement", "Transport & déplacement"),
    ("autre", "Autre"),
]

PRESTATION_UNITE_CHOICES = [
    ("m2", "m²"),
    ("ml", "ml"),
    ("m3", "m³"),
    ("unite", "unité"),
    ("forfait", "forfait"),
    ("heure", "heure"),
    ("jour", "jour"),
    ("kg", "kg"),
]

# ── Sous-Traitance (Casa di Lusso) specific choices ───────────────────────

CONTRACT_CATEGORY_CHOICES = [
    ("standard", "Standard"),
    ("sous_traitance", "Sous-Traitance"),
]

ST_LOT_TYPE_CHOICES = [
    ("gros_oeuvre", "Travaux de Gros Œuvre"),
    ("electricite", "Travaux d'Électricité"),
    ("plomberie", "Travaux de Plomberie et Sanitaire"),
    ("menuiserie_alu", "Travaux de Menuiserie Aluminium"),
    ("menuiserie_bois", "Travaux de Menuiserie Bois"),
    ("carrelage", "Travaux de Carrelage et Faïence"),
    ("peinture", "Travaux de Peinture"),
    ("etancheite", "Travaux d'Étanchéité"),
    ("ascenseur", "Fourniture et Installation d'Ascenseur"),
    ("platre", "Travaux de Plâtre et Faux Plafond"),
    ("ferronnerie", "Travaux de Ferronnerie et Garde-Corps"),
    ("vrd", "Travaux de VRD et Façade"),
    ("climatisation", "Travaux de Climatisation et Ventilation"),
    ("cuisine", "Fourniture et Pose de Cuisines Équipées"),
]

ST_PROJET_TYPE_CHOICES = [
    ("immeuble", "Immeuble"),
    ("villa", "Villa"),
    ("commercial", "Commercial"),
    ("industriel", "Industriel"),
    ("renovation", "Rénovation"),
    ("autre", "Autre"),
]

ST_FORME_JURIDIQUE_CHOICES = [
    ("SARL", "SARL"),
    ("SA", "SA"),
    ("SARLAU", "SARLAU"),
    ("SNC", "SNC"),
    ("auto_entrepreneur", "Auto-entrepreneur"),
    ("personne_physique", "Personne physique"),
]

ST_TYPE_PRIX_CHOICES = [
    ("forfaitaire", "Forfaitaire ferme"),
    ("unitaire", "Prix unitaires"),
    ("regie", "Régie"),
]

ST_DELAI_UNIT_CHOICES = [
    ("mois", "Mois"),
    ("semaines", "Semaines"),
    ("jours", "Jours"),
]
