BL_COMPANY = {
    "name": "BlueLine Works",
    "tagline_fr": "Céramique · Marbre · Finitions · Plans de travail",
    "tagline_en": "Ceramics · Marble · Finishing · Countertops",
    "phone": "+212 5XX XXX XXX",
    "ice": "003852374000069",
    "address": "148 AV MOHAMED V, RESIDENCE NECTAR, ETAGE 1 N°013 – TANGER",
    "email": "worksblueline@gmail.com",
}

FOURNITURES_LABELS = {
    "fr": {
        "non_incluses": "Non incluses dans le présent contrat — à la charge exclusive du client",
        "incluses": "Incluses dans le prix contractuel (voir détail des prestations)",
        "partielles": "Partiellement incluses — se référer au détail des prestations",
    },
    "en": {
        "non_incluses": "Not included in this contract — at the client's expense",
        "incluses": "Included in the contractual price (see service details)",
        "partielles": "Partially included — refer to service details",
    },
}

EAU_ELEC_LABELS = {
    "fr": {
        "client": (
            "Le Client s'engage à mettre à disposition, à ses frais, "
            "l'eau et l'électricité nécessaires à la réalisation des travaux."
        ),
        "entreprise": (
            "BlueLine Works prendra en charge la fourniture de l'eau et de "
            "l'électricité nécessaires à la réalisation des travaux, incluse "
            "dans le prix contractuel."
        ),
        "partage": (
            "La fourniture de l'eau et de l'électricité sera partagée entre "
            "le Client et BlueLine Works selon les disponibilités sur chantier."
        ),
        "selon_cas": (
            "La fourniture de l'eau et de l'électricité sera assurée selon "
            "disponibilité par le Client ou par BlueLine Works, sans impact "
            "sur le prix contractuel."
        ),
    },
    "en": {
        "client": (
            "The Client commits to providing, at their own expense, "
            "the water and electricity necessary for the works."
        ),
        "entreprise": (
            "BlueLine Works will provide the water and electricity "
            "necessary for the works, included in the contractual price."
        ),
        "partage": (
            "The supply of water and electricity will be shared between "
            "the Client and BlueLine Works depending on on-site availability."
        ),
        "selon_cas": (
            "The supply of water and electricity will be provided depending "
            "on availability by the Client or BlueLine Works, with no impact "
            "on the contractual price."
        ),
    },
}

GARANTIE_TYPE_LABELS = {
    "fr": {
        "defauts": "Défauts d'exécution",
        "bonne_fin": "Bonne fin des travaux",
        "decennale": "Garantie décennale",
        "aucune": "Aucune",
    },
    "en": {
        "defauts": "Execution defects",
        "bonne_fin": "Completion of works",
        "decennale": "Ten-year warranty",
        "aucune": "None",
    },
}

GARANTIE_UNITE_LABELS = {
    "fr": {"mois": "mois", "ans_s": "an", "ans_p": "ans"},
    "en": {"mois": "months", "ans_s": "year", "ans_p": "years"},
}

CLAUSE_RESILIATION_LABELS = {
    "fr": {
        "30j": (
            "Le présent contrat peut être résilié par l'une ou l'autre des "
            "parties moyennant un préavis de <strong>30 jours</strong> notifié "
            "par lettre recommandée avec accusé de réception."
        ),
        "15j": (
            "Le présent contrat peut être résilié par l'une ou l'autre des "
            "parties moyennant un préavis de <strong>15 jours</strong> notifié "
            "par lettre recommandée avec accusé de réception."
        ),
        "mutuel": (
            "Le présent contrat ne peut être résilié que d'un "
            "<strong>commun accord écrit</strong> entre les deux parties."
        ),
        "aucune": (
            "Aucune clause de résiliation anticipée n'est prévue dans ce contrat."
        ),
    },
    "en": {
        "30j": (
            "This contract may be terminated by either party with "
            "<strong>30 days</strong> notice sent by registered mail "
            "with acknowledgement of receipt."
        ),
        "15j": (
            "This contract may be terminated by either party with "
            "<strong>15 days</strong> notice sent by registered mail "
            "with acknowledgement of receipt."
        ),
        "mutuel": (
            "This contract may only be terminated by "
            "<strong>mutual written agreement</strong> between both parties."
        ),
        "aucune": "No early termination clause is provided in this contract.",
    },
}

BL_TX = {
    "fr": {
        "contrat_title": "Contrat de Prestations de Travaux",
        "contrat_subtitle": "Pose de carrelage, marbre, finitions et travaux connexes",
        "badge": "CONTRAT DE TRAVAUX",
        "parties_title": "Parties au Contrat",
        "prestataire_label": "Le Prestataire",
        "client_label": "Le Client",
        "prestataire_desc": (
            "Spécialiste en pose de carrelage, marbre,\n"
            "finitions et plans de travail"
        ),
        "chantier_title": "Description du Chantier",
        "prestations_title": "Détail des Prestations & Travaux",
        "paiement_title": "Conditions & Échéancier de Paiement",
        "articles_title": "Conditions Générales & Clauses Contractuelles",
        "signatures_title": "Signatures",
        # Table headers
        "th_designation": "Désignation",
        "th_qty": "Qté",
        "th_pu": "P.U. HT",
        "th_tva": "TVA",
        "th_montant": "Montant HT",
        # Totals
        "subtotal_ht": "Sous-total HT",
        "tva_label": "TVA (20%)",
        "total_ttc": "TOTAL TTC",
        # Payment schedule
        "acompte_label": "Acompte à la commande",
        "tranche2_label": "2ème tranche",
        "solde_label": "Solde à la livraison",
        "acompte_detail": "Dû à la signature du contrat",
        "tranche2_detail": "En cours de chantier",
        "solde_detail": "À la réception & signature PV",
        "mode_paiement": "Mode de paiement",
        "coord_bancaires": "Coordonnées bancaires",
        # Chantier info
        "adresse_chantier": "Adresse chantier",
        "ville": "Ville",
        "type_bien": "Type de bien",
        "surface_totale": "Surface totale",
        "date_debut": "Date de début",
        "fin_estimee": "Fin estimée",
        # Client info
        "adresse": "Adresse",
        "tel": "Tél",
        "email": "Email",
        "cin_ice": "CIN/ICE",
        "ice": "ICE",
        # Signatures
        "fait_a": "Fait à",
        "le": "le",
        "en_deux_ex": "en deux (2) exemplaires originaux, dont un remis à chacune des parties.",
        "sig_cachet": "Signature & Cachet",
        "lu_approuve": '"Lu et approuvé"',
        "date_sig": "Date",
        # Footer
        "footer_specialist": "Spécialiste Pose Céramique, Marbre & Finitions — Plans de travail cuisine",
        "doc_genere": "Document généré le",
        "a": "à",
        "valeur_juridique": "Ce contrat a valeur juridique une fois signé par les deux parties.",
        # Garantie
        "sans_garantie": "Sans garantie",
        "jours_ouvrables": "jours ouvrables",
        # Article titles
        "art1_title": "Article 1 — Objet du contrat",
        "art2_title": "Article 2 — Fournitures & Matériaux",
        "art3_title": "Article 3 — Délais d'exécution",
        "art4_title": "Article 4 — Garantie des travaux",
        "art5_title": "Article 5 — Réception des travaux",
        "art6_title": "Article 6 — Retards de paiement",
        "art7_title": "Article 7 — Résiliation du contrat",
        "art8_title": "Article 8 — Sécurité, accès et obligations du client",
        "art9_title": "Article 9 — Responsabilité & Assurance",
        "art10_title": "Article 10 — Protection des données personnelles",
        "art11_title": "Article 11 — Règlement des litiges & Juridiction",
        "notes_title": "Notes & Observations Particulières",
        # Client info extra
        "qualite": "Qualité",
        "description_travaux_label": "Détail des travaux :",
        # Prestation units
        "aucune_prestation": "Aucune prestation",
    },
    "en": {
        "contrat_title": "Works Service Agreement",
        "contrat_subtitle": "Tiling, marble, finishing and related works",
        "badge": "WORKS CONTRACT",
        "parties_title": "Contract Parties",
        "prestataire_label": "The Service Provider",
        "client_label": "The Client",
        "prestataire_desc": (
            "Specialist in tiling, marble,\n" "finishing and countertops"
        ),
        "chantier_title": "Site Description",
        "prestations_title": "Service Details & Works",
        "paiement_title": "Payment Terms & Schedule",
        "articles_title": "General Terms & Contractual Clauses",
        "signatures_title": "Signatures",
        # Table headers
        "th_designation": "Description",
        "th_qty": "Qty",
        "th_pu": "Unit Price (excl.)",
        "th_tva": "VAT",
        "th_montant": "Amount (excl.)",
        # Totals
        "subtotal_ht": "Subtotal (excl. VAT)",
        "tva_label": "VAT (20%)",
        "total_ttc": "TOTAL (incl. VAT)",
        # Payment schedule
        "acompte_label": "Deposit on order",
        "tranche2_label": "2nd instalment",
        "solde_label": "Balance on delivery",
        "acompte_detail": "Due upon signing the contract",
        "tranche2_detail": "During works",
        "solde_detail": "Upon reception & signing acceptance report",
        "mode_paiement": "Payment method",
        "coord_bancaires": "Bank details",
        # Chantier info
        "adresse_chantier": "Site address",
        "ville": "City",
        "type_bien": "Property type",
        "surface_totale": "Total area",
        "date_debut": "Start date",
        "fin_estimee": "Estimated completion",
        # Client info
        "adresse": "Address",
        "tel": "Phone",
        "email": "Email",
        "cin_ice": "ID/Passport",
        "ice": "ICE",
        # Signatures
        "fait_a": "Done in",
        "le": "on",
        "en_deux_ex": "in two (2) original copies, one provided to each party.",
        "sig_cachet": "Signature & Stamp",
        "lu_approuve": '"Read and approved"',
        "date_sig": "Date",
        # Footer
        "footer_specialist": "Specialist in Ceramic, Marble & Finishing — Kitchen countertops",
        "doc_genere": "Document generated on",
        "a": "at",
        "valeur_juridique": "This contract is legally binding once signed by both parties.",
        # Garantie
        "sans_garantie": "No warranty",
        "jours_ouvrables": "working days",
        # Article titles
        "art1_title": "Article 1 — Purpose of the contract",
        "art2_title": "Article 2 — Supplies & Materials",
        "art3_title": "Article 3 — Execution deadlines",
        "art4_title": "Article 4 — Works guarantee",
        "art5_title": "Article 5 — Reception of works",
        "art6_title": "Article 6 — Late payments",
        "art7_title": "Article 7 — Contract termination",
        "art8_title": "Article 8 — Safety, access and client obligations",
        "art9_title": "Article 9 — Liability & Insurance",
        "art10_title": "Article 10 — Personal data protection",
        "art11_title": "Article 11 — Dispute resolution & Jurisdiction",
        "notes_title": "Notes & Special Observations",
        # Client info extra
        "qualite": "Status",
        "description_travaux_label": "Works details:",
        # Prestation units
        "aucune_prestation": "No services",
    },
}


def bl_t(key: str, lang: str = "fr") -> str:
    """Return translated text for *key* in *lang*."""
    return BL_TX.get(lang, BL_TX["fr"]).get(key, BL_TX["fr"].get(key, key))
