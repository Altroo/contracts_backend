"""
Shared constants used across multiple apps.
"""

from django.utils.translation import gettext_lazy as _

COMPANY_CHOICES = [
    ("casa_di_lusso", _("Casa di Lusso")),
    ("blueline_works", _("Blueline Works")),
]

CURRENCY_CHOICES = [
    ("MAD", _("MAD – Dirham Marocain")),
    ("EUR", _("EUR – Euro")),
    ("USD", _("USD – Dollar Américain")),
]

CONTRACT_TYPE_CHOICES = [
    ("travaux_finition", _("Travaux de Finition")),
    ("travaux_gros_oeuvre", _("Travaux Gros Œuvre")),
    ("design_interieur", _("Design Intérieur")),
    ("cle_en_main", _("Clé en Main")),
    ("ameublement", _("Ameublement")),
    ("maintenance", _("Maintenance")),
    ("suivi_chantier", _("Suivi Chantier")),
]

TYPE_BIEN_CHOICES = [
    ("appartement", _("Appartement")),
    ("villa", _("Villa")),
    ("duplex", _("Duplex")),
    ("residence", _("Résidence")),
    ("hotel", _("Hôtel")),
    ("riad_maison_traditionnelle", _("Riad / Maison Traditionnelle")),
    ("bureau_local_commercial", _("Bureau / Local Commercial")),
    ("commerce_local", _("Commerce / Local")),
    ("hotel_riad_hotelier", _("Hôtel / Riad Hôtelier")),
    ("immeuble", _("Immeuble")),
    ("autre", _("Autre")),
]

CLIENT_QUALITE_CHOICES = [
    ("particulier", _("Particulier")),
    ("entreprise_societe", _("Entreprise / Société")),
    ("investisseur_immobilier", _("Investisseur Immobilier")),
    ("administration_institution", _("Administration / Institution")),
]


GARANTIE_CHOICES = [
    ("1 mois", _("1 mois")),
    ("3 mois", _("3 mois")),
    ("6 mois", _("6 mois")),
    ("1 an", _("1 an")),
    ("2 ans", _("2 ans")),
    ("3 ans", _("3 ans")),
    ("sans_garantie", _("Sans garantie contractuelle")),
]

TRIBUNAL_CHOICES = [
    ("Tanger", _("Tanger")),
    ("Casablanca", _("Casablanca")),
    ("Rabat", _("Rabat")),
    ("Marrakech", _("Marrakech")),
    ("Fès", _("Fès")),
    ("Agadir", _("Agadir")),
]

CONFIDENTIALITE_CHOICES = [
    ("CONFIDENTIEL", _("CONFIDENTIEL")),
    ("USAGE INTERNE", _("USAGE INTERNE")),
    ("STANDARD", _("STANDARD")),
]

STATUT_CHOICES = [
    ("Brouillon", _("Brouillon")),
    ("Envoyé", _("Envoyé")),
    ("Signé", _("Signé")),
    ("En cours", _("En cours")),
    ("Terminé", _("Terminé")),
    ("Annulé", _("Annulé")),
    ("Expiré", _("Expiré")),
]

MODE_PAIEMENT_TEXTE_CHOICES = [
    ("Virement Bancaire", _("Virement Bancaire")),
    ("Chèque Certifié", _("Chèque Certifié")),
    ("Espèces", _("Espèces")),
    ("Paiement Mixte", _("Paiement Mixte")),
    ("Mobile Money", _("Mobile Money")),
    ("Virement ou Chèque", _("Virement ou Chèque")),
]

PENALITE_RETARD_UNITE_CHOICES = [
    ("mad_per_day", _("MAD par jour")),
    ("percent_per_day", _("Pourcentage par jour")),
]

# ── Blueline Works specific choices ────────────────────────────────────────

FOURNITURES_CHOICES = [
    ("non_incluses", _("Non incluses (fournies par le client)")),
    ("incluses", _("Incluses dans le contrat")),
    ("partielles", _("Partiellement incluses")),
]

EAU_ELECTRICITE_CHOICES = [
    ("client", _("À la charge du client")),
    ("entreprise", _("À la charge de l'entreprise")),
    ("partage", _("Partagé")),
    ("selon_cas", _("Selon le cas")),
]

GARANTIE_UNITE_CHOICES = [
    ("mois", _("Mois")),
    ("ans", _("Ans")),
]

GARANTIE_TYPE_CHOICES = [
    ("defauts", _("Garantie des défauts")),
    ("bonne_fin", _("Garantie de bonne fin")),
    ("decennale", _("Garantie décennale")),
    ("aucune", _("Aucune garantie")),
]

CLAUSE_RESILIATION_CHOICES = [
    ("30j", _("Préavis de 30 jours")),
    ("15j", _("Préavis de 15 jours")),
    ("mutuel", _("D'un commun accord")),
    ("aucune", _("Aucune clause")),
]

PRESTATION_NOM_CHOICES = [
    ("pose_carrelage", _("Pose de carrelage")),
    ("pose_marbre", _("Pose de marbre")),
    ("plan_travail_cuisine", _("Plan de travail cuisine")),
    ("revetement_mural_faience", _("Revêtement mural faïence")),
    ("finitions_peinture", _("Finitions peinture")),
    ("pose_parquet", _("Pose de parquet")),
    ("enduit_crepi", _("Enduit & crépi")),
    ("joints_silicone", _("Joints & silicone")),
    ("depose_demolition", _("Dépose & démolition")),
    ("preparation_surfaces", _("Préparation des surfaces")),
    ("seuils_plinthes", _("Seuils & plinthes")),
    ("douche_italienne", _("Douche à l'italienne")),
    ("escalier_marbre", _("Escalier marbre")),
    ("terrasse_exterieure", _("Terrasse extérieure")),
    ("main_oeuvre", _("Main d'œuvre qualifiée")),
    ("transport_deplacement", _("Transport & déplacement")),
    ("autre", _("Autre")),
]

PRESTATION_UNITE_CHOICES = [
    ("m2", _("m²")),
    ("ml", _("ml")),
    ("m3", _("m³")),
    ("unite", _("unité")),
    ("forfait", _("forfait")),
    ("heure", _("heure")),
    ("jour", _("jour")),
    ("kg", _("kg")),
]

# ── Sous-Traitance (Casa di Lusso) specific choices ───────────────────────

CONTRACT_CATEGORY_CHOICES = [
    ("standard", _("Standard")),
    ("sous_traitance", _("Sous-Traitance")),
]

ST_LOT_TYPE_CHOICES = [
    ("gros_oeuvre", _("Travaux de Gros Œuvre")),
    ("electricite", _("Travaux d'Électricité")),
    ("plomberie", _("Travaux de Plomberie et Sanitaire")),
    ("menuiserie_alu", _("Travaux de Menuiserie Aluminium")),
    ("menuiserie_bois", _("Travaux de Menuiserie Bois")),
    ("carrelage", _("Travaux de Carrelage et Faïence")),
    ("peinture", _("Travaux de Peinture")),
    ("etancheite", _("Travaux d'Étanchéité")),
    ("ascenseur", _("Fourniture et Installation d'Ascenseur")),
    ("platre", _("Travaux de Plâtre et Faux Plafond")),
    ("ferronnerie", _("Travaux de Ferronnerie et Garde-Corps")),
    ("vrd", _("Travaux de VRD et Façade")),
    ("climatisation", _("Travaux de Climatisation et Ventilation")),
    ("cuisine", _("Fourniture et Pose de Cuisines Équipées")),
]

ST_PROJET_TYPE_CHOICES = [
    ("immeuble", _("Immeuble")),
    ("villa", _("Villa")),
    ("commercial", _("Commercial")),
    ("industriel", _("Industriel")),
    ("renovation", _("Rénovation")),
    ("autre", _("Autre")),
]

ST_FORME_JURIDIQUE_CHOICES = [
    ("SARL", _("SARL")),
    ("SA", _("SA")),
    ("SARLAU", _("SARLAU")),
    ("SNC", _("SNC")),
    ("auto_entrepreneur", _("Auto-entrepreneur")),
    ("personne_physique", _("Personne physique")),
]

ST_TYPE_PRIX_CHOICES = [
    ("forfaitaire", _("Forfaitaire ferme")),
    ("unitaire", _("Prix unitaires")),
    ("regie", _("Régie")),
]

ST_DELAI_UNIT_CHOICES = [
    ("mois", _("Mois")),
    ("semaines", _("Semaines")),
    ("jours", _("Jours")),
]
