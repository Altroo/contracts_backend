"""
contract/st_i18n.py
~~~~~~~~~~~~~~~~~~~
Bilingual (FR / EN) translations for the Sous-Traitance contract generator.
"""

# ── Lot-type labels ──────────────────────────────────────────────────────────

LOT_LABELS = {
    "fr": {
        "gros_oeuvre": "Travaux de Gros Œuvre",
        "electricite": "Travaux d'Électricité (Courants Forts et Faibles)",
        "plomberie": "Travaux de Plomberie et Sanitaire",
        "menuiserie_alu": "Travaux de Menuiserie Aluminium",
        "menuiserie_bois": "Travaux de Menuiserie Bois",
        "carrelage": "Travaux de Carrelage et Faïence",
        "peinture": "Travaux de Peinture",
        "etancheite": "Travaux d'Étanchéité",
        "ascenseur": "Fourniture et Installation d'Ascenseur",
        "platre": "Travaux de Plâtre et Faux Plafond",
        "ferronnerie": "Travaux de Ferronnerie et Garde-Corps",
        "vrd": "Travaux de VRD et Façade",
        "climatisation": "Travaux de Climatisation et Ventilation",
        "cuisine": "Fourniture et Pose de Cuisines Équipées",
    },
    "en": {
        "gros_oeuvre": "Structural Works",
        "electricite": "Electrical Works (High & Low Voltage)",
        "plomberie": "Plumbing & Sanitary Works",
        "menuiserie_alu": "Aluminium Joinery Works",
        "menuiserie_bois": "Wood Joinery Works",
        "carrelage": "Tiling & Ceramic Works",
        "peinture": "Painting Works",
        "etancheite": "Waterproofing Works",
        "ascenseur": "Elevator Supply & Installation",
        "platre": "Plastering & False Ceiling Works",
        "ferronnerie": "Iron & Railing Works",
        "vrd": "Utilities & Façade Works",
        "climatisation": "HVAC & Ventilation Works",
        "cuisine": "Kitchen Supply & Installation",
    },
}

# ── Trade-specific norms ─────────────────────────────────────────────────────

LOT_NORMES = {
    "gros_oeuvre": "NM 10.1.008 (béton), RPS 2000 (parasismique), DTU 20.1 (maçonnerie), NM 10.1.271 (ciment)",
    "electricite": "NF C 15-100, NM 06.1.001, Règlement AMENDIS/ONEE, normes UTE",
    "plomberie": "DTU 60.1 (plomberie), DTU 60.11 (évacuation), NM 10.9.001, normes AMENDIS",
    "menuiserie_alu": "NF P 24-301, DTU 36.5, NM 06.3.009, label CEKAL (vitrage)",
    "menuiserie_bois": "DTU 36.1, NM 06.2.001, normes AFNOR bois",
    "carrelage": "DTU 52.1 (sols), DTU 55.2 (murs), NM 10.6.001",
    "peinture": "DTU 59.1 (peinture intérieure), DTU 59.2 (extérieure), NM 10.7.001",
    "etancheite": "DTU 43.1 (terrasses), DTU 43.5 (réfection), NM 10.4.001, avis technique CSTB",
    "ascenseur": "NM 10.8.001 (ascenseurs), EN 81-20/50, directive 2014/33/UE",
    "platre": "DTU 25.1 (plâtre), DTU 58.1 (faux plafonds), NM 10.5.001",
    "ferronnerie": "NF P 01-012 (garde-corps), DTU 37.1, NM 10.3.001",
    "vrd": "DTU 64.1, Cahier des prescriptions AMENDIS/ONEP, normes routières marocaines",
    "climatisation": "DTU 68.3 (ventilation), NF EN 378, réglementation thermique marocaine (RTCM)",
    "cuisine": "NF D 60-001, normes de sécurité électrique et gaz applicables",
}

# ── Trade-specific insurance ─────────────────────────────────────────────────

LOT_ASSURANCES = {
    "fr": {
        "gros_oeuvre": "Responsabilité Civile Professionnelle, Garantie Décennale (art. 769 D.O.C.), Assurance Accidents du Travail",
        "electricite": "Responsabilité Civile Professionnelle, Assurance Décennale",
        "plomberie": "Responsabilité Civile Professionnelle, Garantie Décennale (étanchéité réseaux)",
        "menuiserie_alu": "Responsabilité Civile Professionnelle, Garantie Décennale (étanchéité à l'air et à l'eau)",
        "menuiserie_bois": "Responsabilité Civile Professionnelle",
        "carrelage": "Responsabilité Civile Professionnelle",
        "peinture": "Responsabilité Civile Professionnelle",
        "etancheite": "Responsabilité Civile Professionnelle, Garantie Décennale (obligatoire étanchéité)",
        "ascenseur": "Responsabilité Civile Professionnelle, Garantie Décennale, Assurance maintenance",
        "platre": "Responsabilité Civile Professionnelle",
        "ferronnerie": "Responsabilité Civile Professionnelle",
        "vrd": "Responsabilité Civile Professionnelle",
        "climatisation": "Responsabilité Civile Professionnelle, Garantie Décennale",
        "cuisine": "Responsabilité Civile Professionnelle",
    },
    "en": {
        "gros_oeuvre": "Professional Liability Insurance, Ten-Year Warranty (art. 769 D.O.C.), Work Accident Insurance",
        "electricite": "Professional Liability Insurance, Ten-Year Warranty",
        "plomberie": "Professional Liability Insurance, Ten-Year Warranty (network waterproofing)",
        "menuiserie_alu": "Professional Liability Insurance, Ten-Year Warranty (air and water tightness)",
        "menuiserie_bois": "Professional Liability Insurance",
        "carrelage": "Professional Liability Insurance",
        "peinture": "Professional Liability Insurance",
        "etancheite": "Professional Liability Insurance, Ten-Year Warranty (mandatory waterproofing)",
        "ascenseur": "Professional Liability Insurance, Ten-Year Warranty, Maintenance Insurance",
        "platre": "Professional Liability Insurance",
        "ferronnerie": "Professional Liability Insurance",
        "vrd": "Professional Liability Insurance",
        "climatisation": "Professional Liability Insurance, Ten-Year Warranty",
        "cuisine": "Professional Liability Insurance",
    },
}

# ── Trade-specific default descriptions ──────────────────────────────────────

LOT_DESC_DEFAULT = {
    "fr": {
        "gros_oeuvre": (
            "Travaux de structure béton armé comprenant : terrassement, fondations (semelles et longrines), "
            "murs de soutènement, poteaux, poutres, dalles, escaliers, maçonnerie (double cloison extérieure "
            "et cloisons intérieures), enduits intérieurs et extérieurs, acrotères, conformément aux plans "
            "d'exécution visés par le BET et le BCT."
        ),
        "electricite": (
            "Installation électrique complète comprenant : TGBT, tableaux divisionnaires par logement, "
            "câblage courants forts (éclairage et prises), câblage courants faibles (TV, téléphone, "
            "interphone, pré-câblage fibre optique), appareillage, éclairage des parties communes, "
            "paratonnerre et mise à la terre, vidéosurveillance des parties communes."
        ),
        "plomberie": (
            "Travaux de plomberie sanitaire comprenant : réseaux d'alimentation eau froide et eau chaude "
            "(multicouche/cuivre), réseaux d'évacuation EU/EV (PVC), colonnes montantes et descentes, "
            "pose des appareils sanitaires (WC, lavabos, baignoires/douches), robinetterie, chauffe-eau, "
            "réseau incendie (colonnes sèches et RIA)."
        ),
        "menuiserie_alu": (
            "Fourniture et pose de menuiseries aluminium comprenant : fenêtres coulissantes avec double "
            "vitrage (4/12/4), baies vitrées des séjours, châssis fixes, volets roulants le cas échéant, "
            "habillage des tableaux et appuis, joints d'étanchéité EPDM, quincaillerie complète."
        ),
        "menuiserie_bois": (
            "Fourniture et pose de menuiseries bois comprenant : portes d'entrée blindées des appartements, "
            "portes intérieures isoplane, portes de SDB hydrofuges, placards intégrés avec étagères et "
            "penderies, huisseries et chambranles, quincaillerie complète."
        ),
        "carrelage": (
            "Travaux de revêtement comprenant : carrelage sol des appartements (1er choix 40×40 ou 60×60), "
            "carrelage sol magasins, carrelage parties communes et escaliers (granito ou marbre local), "
            "faïence murale complète des SDB (H=2,20m), crédence cuisines, seuils et appuis en marbre, "
            "plinthes assorties."
        ),
        "peinture": (
            "Travaux de peinture comprenant : peinture intérieure des murs (vinylique 2 couches sur enduit), "
            "peinture des plafonds (blanc mat), peinture extérieure des façades (acrylique 2 couches sur "
            "sous-couche), peinture des parties communes (peinture lavable), traitement des boiseries et "
            "menuiseries si nécessaire."
        ),
        "etancheite": (
            "Travaux d'étanchéité comprenant : étanchéité multicouche de la toiture terrasse (bitume "
            "élastomère + protection), étanchéité des terrasses accessibles des retraits (membrane + carrelage "
            "sur plots), cuvelage du sous-sol (murs + radier), étanchéité sous carrelage des SDB (membrane liquide)."
        ),
        "ascenseur": (
            "Fourniture, installation et mise en service d'un ascenseur comprenant : 1 cabine de 6 personnes "
            "(450 kg), 8 arrêts (sous-sol à 2ème retrait), motorisation à variation de fréquence, portes "
            "palières automatiques, boutons d'appel à chaque palier, dispositif de sécurité complet "
            "(parachute, limiteur de vitesse, éclairage de secours), finition cabine moyen standing."
        ),
        "platre": (
            "Travaux de plâtrerie comprenant : faux plafond en plaques de plâtre BA13 dans les SDB et "
            "cuisines (BA13 hydrofuge), faux plafond décoratif du hall d'entrée, corniches et moulures "
            "en plâtre dans les appartements, finition des joues et habillages techniques."
        ),
        "ferronnerie": (
            "Fourniture et pose d'ouvrages métalliques comprenant : garde-corps de balcons et terrasses "
            "(hauteur réglementaire 1m), rampes d'escalier, grilles de ventilation, portillon de parking, "
            "éléments décoratifs métalliques selon plans de l'architecte."
        ),
        "vrd": (
            "Travaux de voiries et réseaux divers comprenant : branchements réseaux (eau potable, "
            "assainissement, électricité, télécom), aménagement du parking sous-sol (béton lissé + marquage), "
            "revêtement et habillage de la façade extérieure, portail motorisé, espaces verts et clôture, "
            "signalétique de l'immeuble."
        ),
        "climatisation": (
            "Fourniture et installation de systèmes de climatisation comprenant : unités split ou multi-split "
            "par appartement, pré-installation des conduites de fluides frigorigènes, réseau de gaines de "
            "ventilation, VMC dans les pièces humides, extraction mécanique dans les parkings souterrains."
        ),
        "cuisine": (
            "Fourniture et pose de cuisines équipées comprenant : meubles bas et hauts en mélaminé ou "
            "stratifié, plan de travail en granit ou quartz, évier inox avec mitigeur, raccordements eau "
            "et évacuation, installation électrique des équipements encastrables, crédence."
        ),
    },
    "en": {
        "gros_oeuvre": (
            "Reinforced concrete structural works including: earthworks, foundations (footings and tie beams), "
            "retaining walls, columns, beams, slabs, staircases, masonry (double external walls and internal "
            "partitions), interior and exterior plaster, parapets, in accordance with execution plans approved "
            "by the structural engineer and technical inspectorate."
        ),
        "electricite": (
            "Complete electrical installation including: main switchboard, distribution boards per unit, "
            "high voltage wiring (lighting and outlets), low voltage wiring (TV, telephone, intercom, "
            "fibre optic pre-wiring), fixtures, common area lighting, lightning rod and earthing, "
            "CCTV for common areas."
        ),
        "plomberie": (
            "Plumbing and sanitary works including: cold and hot water supply networks (multilayer/copper), "
            "waste and soil water drainage networks (PVC), risers and downpipes, installation of sanitary "
            "fixtures (WC, washbasins, bathtubs/showers), taps, water heaters, fire-fighting network "
            "(dry risers and hose reels)."
        ),
        "menuiserie_alu": (
            "Supply and installation of aluminium joinery including: sliding windows with double glazing "
            "(4/12/4), living room bay windows, fixed frames, roller shutters where applicable, "
            "reveals and sills cladding, EPDM weatherseals, complete hardware."
        ),
        "menuiserie_bois": (
            "Supply and installation of wood joinery including: armoured apartment entrance doors, "
            "flush interior doors, moisture-resistant bathroom doors, built-in wardrobes with shelves "
            "and hanging rails, frames and architraves, complete hardware."
        ),
        "carrelage": (
            "Tiling works including: apartment floor tiles (1st grade 40×40 or 60×60), shop floor tiles, "
            "common areas and stairs tiles (terrazzo or local marble), full bathroom wall tiles (H=2.20m), "
            "kitchen splashbacks, marble thresholds and sills, matching skirting boards."
        ),
        "peinture": (
            "Painting works including: interior wall paint (vinyl 2 coats on plaster), ceiling paint "
            "(matt white), exterior façade paint (acrylic 2 coats on primer), common areas paint "
            "(washable), woodwork and joinery treatment as needed."
        ),
        "etancheite": (
            "Waterproofing works including: multi-layer roof terrace waterproofing (elastomeric bitumen "
            "+ protection), accessible setback terrace waterproofing (membrane + tiles on pedestals), "
            "basement tanking (walls + raft), bathroom under-tile waterproofing (liquid membrane)."
        ),
        "ascenseur": (
            "Supply, installation and commissioning of an elevator including: 1 cabin for 6 persons "
            "(450 kg), 8 stops (basement to 2nd setback), variable frequency drive, automatic landing "
            "doors, call buttons at each floor, complete safety devices (parachute, speed limiter, "
            "emergency lighting), mid-range cabin finish."
        ),
        "platre": (
            "Plastering works including: BA13 plasterboard false ceiling in bathrooms and kitchens "
            "(moisture-resistant BA13), decorative false ceiling in the entrance hall, cornices and "
            "plaster mouldings in apartments, cheek and technical cladding finishes."
        ),
        "ferronnerie": (
            "Supply and installation of metalwork including: balcony and terrace railings (regulatory "
            "height 1m), staircase handrails, ventilation grilles, parking gate, decorative metalwork "
            "elements as per architect's plans."
        ),
        "vrd": (
            "Utilities and external works including: network connections (drinking water, sewage, "
            "electricity, telecom), basement parking layout (smooth concrete + markings), exterior "
            "façade cladding, motorised gate, landscaping and fencing, building signage."
        ),
        "climatisation": (
            "Supply and installation of HVAC systems including: split or multi-split units per apartment, "
            "refrigerant pipe pre-installation, ventilation duct network, CMV in wet rooms, mechanical "
            "extraction in underground parking."
        ),
        "cuisine": (
            "Supply and installation of fitted kitchens including: base and wall units in melamine or "
            "laminate, granite or quartz worktop, stainless steel sink with mixer tap, water and waste "
            "connections, electrical installation for built-in appliances, splashback."
        ),
    },
}

# ── Trade-specific obligations ───────────────────────────────────────────────

LOT_OBLIGATIONS = {
    "fr": {
        "gros_oeuvre": [
            "Respecter scrupuleusement les plans d'exécution du Bureau d'Études Techniques (BET) et les notes de calcul béton armé",
            "Assurer la conformité aux normes parasismiques RPS 2000 en vigueur au Maroc",
            "Réaliser les essais de résistance du béton (éprouvettes 7j et 28j) auprès d'un laboratoire agréé",
            "Tenir un carnet de chantier et un journal des bétonnages",
            "Ne procéder au décoffrage qu'après les délais réglementaires et avec l'accord du BET",
            "Assurer le ferraillage conformément aux plans avec contrôle avant chaque coulage",
            "Fournir les bons de livraison du béton prêt à l'emploi (BPE) avec classe de résistance",
        ],
        "electricite": [
            "Obtenir le certificat de conformité CONSUEL / AMENDIS avant raccordement",
            "Réaliser les essais d'isolement et de continuité selon les normes en vigueur",
            "Fournir les schémas unifilaires et plans de repérage définitifs",
            "Dimensionner les protections (disjoncteurs, différentiels) conformément à la norme NF C 15-100",
            "Assurer la mise à la terre de l'ensemble de l'installation",
            "Livrer un dossier des ouvrages exécutés (DOE) complet",
        ],
        "plomberie": [
            "Réaliser les épreuves d'étanchéité sous pression (10 bars pendant 30 minutes) avant encastrement",
            "Respecter les pentes réglementaires d'évacuation (1 à 3 cm/ml)",
            "Assurer l'isolation acoustique des colonnes d'évacuation en parties communes",
            "Fournir les fiches techniques de tous les appareils et équipements installés",
            "Prévoir les vannes d'isolement par appartement et par colonne",
            "Réaliser les raccordements conformément aux prescriptions d'AMENDIS",
        ],
        "menuiserie_alu": [
            "Fournir des profilés aluminium à rupture de pont thermique certifiés",
            "Garantir les performances d'étanchéité à l'air et à l'eau (classement AEV)",
            "Poser des vitrages conformes au label CEKAL avec certificat",
            "Assurer les calfeutrements et l'étanchéité périphérique",
            "Fournir les PV d'essais AEV des menuiseries",
            "Assurer la protection des ouvrages pendant les travaux de finition",
        ],
        "menuiserie_bois": [
            "Utiliser du bois traité contre les insectes xylophages et les champignons",
            "Assurer l'assemblage des portes avec quincaillerie de qualité (serrures 3 points pour les portes blindées)",
            "Respecter les jeux de fonctionnement réglementaires",
            "Appliquer les traitements de finition (vernis, peinture ou lasure) avant livraison",
            "Fournir les certificats de traitement du bois",
            "Assurer la pose à niveau et d'aplomb de toutes les huisseries",
        ],
        "carrelage": [
            "Vérifier la planéité du support avant pose (tolérance 5mm sous règle de 2m)",
            "Réaliser une pose collée avec mortier-colle adapté au format et au type de carreau",
            "Respecter les joints de fractionnement tous les 40m² maximum",
            "Assurer les coupes droites et les découpes soignées autour des équipements",
            "Réaliser les joints au coulis avec finition propre",
            "Protéger les ouvrages posés jusqu'à la livraison",
        ],
        "peinture": [
            "Préparer les supports : rebouchage, ponçage, application d'un primaire d'accrochage",
            "Appliquer au minimum deux couches croisées après sous-couche",
            "Utiliser des peintures certifiées (faible teneur en COV)",
            "Protéger les menuiseries, vitres, carrelages et tous les ouvrages adjacents",
            "Assurer une finition uniforme sans coulures, traces de reprise ou différences de teinte",
            "Fournir les fiches techniques et les références exactes des peintures utilisées",
        ],
        "etancheite": [
            "Fournir l'avis technique du système d'étanchéité utilisé",
            "Respecter les relevés d'étanchéité en périphérie (hauteur minimum 15 cm)",
            "Réaliser les essais d'étanchéité à l'eau (mise en eau 48h) avant protection",
            "Assurer les raccords avec les évacuations EP et les traversées de dalle",
            "Poser une protection mécanique adaptée à l'usage de la terrasse",
            "Garantir l'étanchéité pendant une durée minimum de 10 ans (garantie décennale)",
        ],
        "ascenseur": [
            "Fournir les plans d'implantation de la gaine et de la machinerie pour validation par le BET",
            "Assurer la conformité aux normes EN 81-20/50 et à la réglementation marocaine",
            "Réaliser les essais de réception par un organisme de contrôle agréé",
            "Fournir le dossier technique complet (plans, schémas, notices d'entretien)",
            "Assurer la formation du personnel de maintenance du syndic",
            "Proposer un contrat de maintenance préventive pour les 2 premières années",
        ],
        "platre": [
            "Utiliser des plaques BA13 hydrofuges (vertes) dans les pièces humides (SDB, cuisines)",
            "Assurer la mise en œuvre sur ossature métallique conformément au DTU 25.41",
            "Respecter les joints de dilatation et les raccords avec les cloisons",
            "Réaliser les trappe de visite pour accès aux réseaux en faux plafond",
            "Assurer la planéité du faux plafond (tolérance 2mm sous règle de 2m)",
            "Fournir un ouvrage prêt à peindre (enduit + ponçage)",
        ],
        "ferronnerie": [
            "Respecter la hauteur réglementaire des garde-corps (1m minimum, 1,20m si hauteur de chute > 6m)",
            "Assurer l'espacement des barreaux conforme à la norme (max 11 cm entre axes)",
            "Appliquer un traitement anticorrosion (galvanisation ou métallisation + peinture)",
            "Fournir les plans d'atelier pour validation avant fabrication",
            "Assurer la fixation par scellement chimique ou mécanique selon le support",
            "Garantir la solidité des ouvrages (résistance à une poussée de 100 daN/ml)",
        ],
        "vrd": [
            "Obtenir les autorisations de raccordement auprès d'AMENDIS et de l'ONEE",
            "Respecter les profondeurs d'enfouissement réglementaires des réseaux",
            "Assurer les regards de visite et de branchement conformes aux normes",
            "Réaliser les essais d'étanchéité des réseaux d'assainissement",
            "Coordonner les travaux avec les concessionnaires (eau, électricité, télécom)",
            "Assurer la remise en état des voiries après travaux de raccordement",
        ],
        "climatisation": [
            "Dimensionner les installations selon le bilan thermique de chaque local",
            "Utiliser des fluides frigorigènes conformes à la réglementation environnementale en vigueur",
            "Assurer l'isolation thermique des conduites frigorifiques",
            "Réaliser les essais de mise en service et les mesures de débit d'air",
            "Fournir les fiches techniques et certificats de conformité des équipements",
            "Prévoir les supports antivibratiles pour les groupes extérieurs",
        ],
        "cuisine": [
            "Effectuer le relevé de cotes précis avant fabrication",
            "Utiliser des matériaux résistants à l'humidité et à la chaleur (classement E1 minimum)",
            "Assurer les raccordements eau, électricité et gaz conformément aux normes",
            "Fournir les garanties fabricant sur les meubles et équipements",
            "Assurer la pose à niveau avec ajustement des pieds et fixation murale sécurisée",
            "Livrer un ouvrage complet avec quincaillerie, charnières et tiroirs fonctionnels",
        ],
    },
    "en": {
        "gros_oeuvre": [
            "Strictly follow the structural engineer's execution plans and reinforced concrete calculation notes",
            "Ensure compliance with the RPS 2000 seismic standards in force in Morocco",
            "Carry out concrete strength tests (7-day and 28-day test specimens) at an accredited laboratory",
            "Maintain a site logbook and a concreting journal",
            "Do not proceed with formwork removal until regulatory periods have elapsed with structural engineer approval",
            "Ensure reinforcement in accordance with plans with inspection before each pour",
            "Provide delivery notes for ready-mixed concrete (RMC) with strength class",
        ],
        "electricite": [
            "Obtain the CONSUEL / AMENDIS compliance certificate before connection",
            "Carry out insulation and continuity tests in accordance with applicable standards",
            "Provide final single-line diagrams and identification plans",
            "Size protections (circuit breakers, RCDs) in accordance with NF C 15-100",
            "Ensure earthing of the entire installation",
            "Deliver a complete as-built dossier (DOE)",
        ],
        "plomberie": [
            "Carry out pressure watertightness tests (10 bar for 30 minutes) before concealment",
            "Comply with regulatory drainage slopes (1 to 3 cm/m)",
            "Ensure acoustic insulation of drainage stacks in common areas",
            "Provide technical data sheets for all installed equipment",
            "Provide isolation valves per apartment and per stack",
            "Make connections in accordance with AMENDIS specifications",
        ],
        "menuiserie_alu": [
            "Supply certified thermal-break aluminium profiles",
            "Guarantee air and water tightness performance (AEV classification)",
            "Install CEKAL-certified glazing with certificate",
            "Ensure caulking and peripheral weatherproofing",
            "Provide AEV test reports for the joinery",
            "Protect works during finishing trades",
        ],
        "menuiserie_bois": [
            "Use timber treated against wood-boring insects and fungi",
            "Assemble doors with quality hardware (3-point locks for armoured doors)",
            "Comply with regulatory operating clearances",
            "Apply finishing treatments (varnish, paint or stain) before delivery",
            "Provide timber treatment certificates",
            "Ensure level and plumb installation of all frames",
        ],
        "carrelage": [
            "Check substrate flatness before laying (5mm tolerance under 2m straightedge)",
            "Carry out bonded installation with tile adhesive suited to format and type",
            "Observe movement joints every 40m² maximum",
            "Ensure straight cuts and neat cuts around fittings",
            "Grout joints with clean finish",
            "Protect laid works until handover",
        ],
        "peinture": [
            "Prepare substrates: filling, sanding, primer application",
            "Apply at least two cross coats after undercoat",
            "Use certified paints (low VOC content)",
            "Protect joinery, glass, tiles and all adjacent works",
            "Ensure uniform finish without runs, overlap marks or colour differences",
            "Provide technical data sheets and exact paint references used",
        ],
        "etancheite": [
            "Provide the technical approval for the waterproofing system used",
            "Comply with perimeter upstands (minimum height 15 cm)",
            "Carry out water-tightness tests (48h flooding) before protection",
            "Ensure connections with rainwater outlets and slab penetrations",
            "Install mechanical protection suited to the terrace use",
            "Guarantee waterproofing for a minimum of 10 years (ten-year warranty)",
        ],
        "ascenseur": [
            "Provide shaft and machine room layout plans for structural engineer approval",
            "Ensure compliance with EN 81-20/50 and Moroccan regulations",
            "Carry out acceptance tests by an accredited inspection body",
            "Provide a complete technical dossier (plans, diagrams, maintenance manuals)",
            "Provide training for syndicate maintenance staff",
            "Offer a preventive maintenance contract for the first 2 years",
        ],
        "platre": [
            "Use moisture-resistant BA13 boards (green) in wet rooms (bathrooms, kitchens)",
            "Install on a metal framework in accordance with DTU 25.41",
            "Observe expansion joints and connections with partitions",
            "Install access hatches for services in the false ceiling",
            "Ensure false ceiling flatness (2mm tolerance under 2m straightedge)",
            "Deliver a surface ready for painting (plaster + sanding)",
        ],
        "ferronnerie": [
            "Comply with regulatory railing height (1m minimum, 1.20m if fall height > 6m)",
            "Ensure bar spacing compliant with standards (max 11 cm between centres)",
            "Apply anti-corrosion treatment (galvanising or metalising + paint)",
            "Provide workshop drawings for approval before fabrication",
            "Ensure fixing by chemical or mechanical anchoring according to substrate",
            "Guarantee structural strength (resistance to 100 daN/m thrust)",
        ],
        "vrd": [
            "Obtain connection authorisations from AMENDIS and ONEE",
            "Comply with regulatory burial depths for networks",
            "Provide inspection chambers and connections compliant with standards",
            "Carry out watertightness tests on sewage networks",
            "Coordinate works with utility companies (water, electricity, telecom)",
            "Restore roadways after connection works",
        ],
        "climatisation": [
            "Size installations according to the thermal balance of each room",
            "Use refrigerants compliant with applicable environmental regulations",
            "Ensure thermal insulation of refrigerant pipes",
            "Carry out commissioning tests and airflow measurements",
            "Provide technical data sheets and equipment compliance certificates",
            "Provide anti-vibration mounts for outdoor units",
        ],
        "cuisine": [
            "Carry out precise dimensional survey before fabrication",
            "Use moisture and heat resistant materials (E1 classification minimum)",
            "Make water, electrical and gas connections in accordance with standards",
            "Provide manufacturer's warranties on furniture and equipment",
            "Ensure level installation with foot adjustment and secure wall fixing",
            "Deliver a complete unit with hardware, hinges and functional drawers",
        ],
    },
}

# ── Trade-specific reception criteria ────────────────────────────────────────

LOT_RECEPTION = {
    "fr": {
        "gros_oeuvre": "La réception sera prononcée après vérification de la résistance structurelle, contrôle des aplombs, des niveaux et de la conformité aux plans.",
        "electricite": "La réception sera subordonnée à la présentation du certificat de conformité et aux résultats satisfaisants des essais d'isolement et de fonctionnement de l'ensemble des circuits.",
        "plomberie": "La réception sera subordonnée aux épreuves d'étanchéité satisfaisantes, au bon fonctionnement de l'ensemble des appareils et à la conformité des raccordements.",
        "menuiserie_alu": "La réception sera subordonnée aux essais d'étanchéité et de manœuvrabilité de chaque ouvrant, et à la vérification du classement AEV.",
        "menuiserie_bois": "La réception portera sur le fonctionnement des ouvrants, la qualité des finitions, l'aplomb des huisseries et la solidité des assemblages.",
        "carrelage": "La réception portera sur la planéité, l'alignement des joints, l'absence de carreaux sonnant creux, la qualité des coupes et la propreté des joints.",
        "peinture": "La réception portera sur l'uniformité des teintes, l'absence de traces de reprise, la couverture du support et la propreté des raccords.",
        "etancheite": "La réception sera subordonnée aux essais de mise en eau concluants (48h sans infiltration) et à la vérification des relevés et des raccords.",
        "ascenseur": "La réception sera prononcée après les essais de fonctionnement, la vérification des dispositifs de sécurité et la présentation du PV de conformité par un organisme agréé.",
        "platre": "La réception portera sur la planéité, la solidité de la fixation, le traitement des joints et la qualité de la surface prête à peindre.",
        "ferronnerie": "La réception portera sur la solidité des fixations, la conformité dimensionnelle, la qualité du traitement anticorrosion et l'aspect esthétique.",
        "vrd": "La réception sera subordonnée à la présentation des PV de conformité des concessionnaires et aux essais satisfaisants des réseaux.",
        "climatisation": "La réception sera subordonnée aux essais de fonctionnement, mesures de température et débit, et à la conformité des installations aux normes.",
        "cuisine": "La réception portera sur la conformité dimensionnelle, la solidité des fixations, le bon fonctionnement de la quincaillerie et la qualité des finitions.",
    },
    "en": {
        "gros_oeuvre": "Acceptance shall be pronounced after verification of structural strength, plumb and level checks, and conformity with plans.",
        "electricite": "Acceptance shall be subject to presentation of the compliance certificate and satisfactory results of insulation and operation tests of all circuits.",
        "plomberie": "Acceptance shall be subject to satisfactory watertightness tests, proper operation of all fixtures and compliance of connections.",
        "menuiserie_alu": "Acceptance shall be subject to watertightness and operability tests of each opening, and verification of AEV classification.",
        "menuiserie_bois": "Acceptance shall cover operation of openings, finish quality, plumb of frames and strength of assemblies.",
        "carrelage": "Acceptance shall cover flatness, joint alignment, absence of hollow-sounding tiles, cut quality and joint cleanliness.",
        "peinture": "Acceptance shall cover colour uniformity, absence of overlap marks, substrate coverage and neatness of junctions.",
        "etancheite": "Acceptance shall be subject to conclusive flooding tests (48h without infiltration) and verification of upstands and connections.",
        "ascenseur": "Acceptance shall be pronounced after operation tests, verification of safety devices and presentation of the compliance report by an accredited body.",
        "platre": "Acceptance shall cover flatness, fixing strength, joint treatment and surface quality ready for painting.",
        "ferronnerie": "Acceptance shall cover fixing strength, dimensional compliance, anti-corrosion treatment quality and aesthetic appearance.",
        "vrd": "Acceptance shall be subject to presentation of utility compliance reports and satisfactory network tests.",
        "climatisation": "Acceptance shall be subject to operation tests, temperature and airflow measurements, and compliance of installations with standards.",
        "cuisine": "Acceptance shall cover dimensional compliance, fixing strength, hardware operation and finish quality.",
    },
}

# ── Forme juridique labels ───────────────────────────────────────────────────

FORME_LABELS = {
    "fr": {
        "SARL": "Société à Responsabilité Limitée (SARL)",
        "SA": "Société Anonyme (SA)",
        "SARLAU": "Société à Responsabilité Limitée d'Associé Unique (SARLAU)",
        "SNC": "Société en Nom Collectif (SNC)",
        "auto_entrepreneur": "Auto-Entrepreneur",
        "personne_physique": "Personne Physique",
    },
    "en": {
        "SARL": "Limited Liability Company (SARL)",
        "SA": "Public Limited Company (SA)",
        "SARLAU": "Sole-Shareholder Limited Liability Company (SARLAU)",
        "SNC": "General Partnership (SNC)",
        "auto_entrepreneur": "Self-Employed",
        "personne_physique": "Natural Person",
    },
}

# ── Type de prix labels ──────────────────────────────────────────────────────

TYPE_PRIX_LABELS = {
    "fr": {
        "forfaitaire": "Forfaitaire, ferme et non révisable",
        "unitaire": "Prix unitaires sur bordereau",
        "regie": "Régie contrôlée",
    },
    "en": {
        "forfaitaire": "Lump sum, firm and non-revisable",
        "unitaire": "Unit prices per schedule",
        "regie": "Controlled cost-plus",
    },
}

# ── Délai unit labels ────────────────────────────────────────────────────────

DELAI_UNIT_LABELS = {
    "fr": {"mois": "mois", "semaines": "semaines", "jours": "jours"},
    "en": {"mois": "months", "semaines": "weeks", "jours": "days"},
}

# ── Main translation dict ────────────────────────────────────────────────────

ST_TX = {
    "fr": {
        "contrat_title": "CONTRAT DE SOUS-TRAITANCE",
        "preamble": (
            "Établi en application des dispositions du Dahir du 12 août 1913 "
            "formant Code des Obligations et des Contrats (D.O.C.) et des "
            "articles 86 à 91 du Code du Travail marocain"
        ),
        "entre": "ENTRE LES SOUSSIGNÉS :",
        "lbl_ep": "L'ENTREPRENEUR PRINCIPAL",
        "lbl_st": "LE SOUS-TRAITANT",
        "ci_ep": "Ci-après dénommé « L'Entrepreneur Principal » ou « EP »",
        "ci_st": "Ci-après dénommé « Le Sous-Traitant » ou « ST »",
        "parties_ensemble": "Ensemble désignées « Les Parties ».",
        "et": "ET",
        "fait_a": "Fait à",
        "le": "le",
        "en_exemplaires": "en deux (2) exemplaires originaux, un pour chaque partie.",
        "lu_approuve": "Lu et approuvé — Signature et cachet",
        "paraphes": "Chaque page du présent contrat doit être paraphée par les deux Parties. Les annexes font partie intégrante du contrat.",
        "page_x_sur_y": "Page {page} sur {pages}",
        "projet": "Projet",
        "ref": "Réf.",
        "date_label": "Date :",
        # Article 1 – Parties
        "art_parties": "PARTIES CONTRACTANTES",
        "partie_ep_title": "1.1 — L'Entrepreneur Principal",
        "partie_st_title": "1.2 — Le Sous-Traitant",
        "raison_sociale": "Raison sociale",
        "forme_juridique": "Forme juridique",
        "capital_social": "Capital social",
        "rc": "Registre de Commerce",
        "ice": "ICE",
        "if_label": "Identifiant Fiscal",
        "cnss": "CNSS",
        "siege": "Siège social",
        "representant": "Représentant légal",
        "qualite": "Qualité",
        "cin": "CIN",
        "telephone": "Téléphone",
        "email": "Email",
        "rib": "RIB",
        "banque": "Banque",
        # Article 2 – Objet
        "art_objet": "OBJET DU CONTRAT",
        "objet_intro": (
            "Le présent contrat a pour objet de confier au Sous-Traitant, sous la responsabilité de l'Entrepreneur Principal "
            "et conformément à l'article 723 et suivants du D.O.C. relatifs au louage d'ouvrage, "
            "l'exécution des travaux de :"
        ),
        "objet_projet": "Projet :",
        "objet_adresse": "Adresse :",
        "objet_mo": "Maître d'ouvrage :",
        "objet_permis": "Permis de construire n° :",
        "objet_normes": "Normes applicables :",
        "objet_declaration": "Le Sous-Traitant déclare avoir pris connaissance de l'ensemble des documents du projet, des plans d'exécution et du cahier des charges, et les accepte sans réserve.",
        # Article 3 – Documents contractuels
        "art_docs": "DOCUMENTS CONTRACTUELS",
        "docs_intro": "Les documents contractuels sont, par ordre de priorité décroissante :",
        "docs_list": [
            "Le présent contrat et ses annexes",
            "Le Cahier des Clauses Techniques Particulières (CCTP) du lot",
            "Le Cahier des Clauses Administratives Particulières (CCAP)",
            "Les plans d'exécution visés « Bon Pour Exécution » (BPE)",
            "Le devis descriptif et quantitatif du Sous-Traitant",
            "Le planning général d'exécution",
            "Les normes et réglementations applicables",
            "Les règles de l'art et les DTU applicables au lot",
        ],
        "docs_contradiction": "En cas de contradiction entre les documents, l'ordre de priorité ci-dessus prévaudra.",
        # Article 4 – Prix et conditions financières
        "art_prix": "PRIX ET CONDITIONS FINANCIÈRES",
        "prix_montant": "4.1 — Montant du marché",
        "prix_type": "Type de prix :",
        "prix_comprend": "Ce prix comprend l'ensemble des fournitures, la main-d'œuvre, le transport, les assurances, les moyens matériels, les frais généraux, les bénéfices et tous frais accessoires nécessaires à la bonne exécution des travaux.",
        "prix_ht": "Montant Hors Taxes (HT) :",
        "prix_tva": "TVA ({tva}%) :",
        "prix_ttc": "Montant Toutes Taxes Comprises (TTC) :",
        "prix_arrete": "Arrêté à la somme de :",
        "prix_modalites": "4.2 — Modalités de paiement",
        "prix_virement_intro": "Le paiement sera effectué par virement bancaire{rib_info} selon l'échéancier ci-dessous :",
        "prix_delai_paiement": "Chaque situation de travaux sera présentée en trois (3) exemplaires, accompagnée des attachements signés. Le délai de paiement est fixé à {days} jours à compter de la réception de la facture conforme, conformément aux usages commerciaux et à l'article 78 du Code de Commerce marocain.",
        "prix_avance": "4.3 — Avance forfaitaire",
        "prix_avance_text": "Une avance forfaitaire de {pct}% du montant HT, soit {amount}, sera versée au Sous-Traitant à la signature du contrat, sur présentation d'une caution de restitution d'avance émise par une banque agréée au Maroc. Cette avance sera déduite proportionnellement sur chaque situation de travaux.",
        "prix_retenue": "4.4 — Retenue de garantie",
        "prix_retenue_text": "Une retenue de garantie de {pct}% sera prélevée sur chaque situation de travaux. Elle sera libérée à l'expiration du délai de garantie de {months} mois, déduction faite des réserves non levées. Le Sous-Traitant pourra substituer cette retenue par une caution bancaire de même montant, émise par un établissement de crédit agréé au Maroc.",
        "prix_supplementaires": "4.5 — Travaux supplémentaires",
        "prix_supplementaires_text": "Aucune prestation supplémentaire ne pourra être facturée sans un ordre de service écrit et signé préalablement par l'Entrepreneur Principal. Tout travail exécuté sans accord écrit préalable ne donnera lieu à aucune rémunération complémentaire.",
        # Article 5 – Délais
        "art_delais": "DÉLAIS D'EXÉCUTION",
        "delais_global": "5.1 — Délai global",
        "delais_global_text": "Le délai global d'exécution des travaux est fixé à {val} {unit} à compter de la date de notification de l'ordre de service de commencement.",
        "delais_planning": "5.2 — Planning",
        "delais_planning_text": "Le Sous-Traitant s'engage à respecter le planning détaillé annexé au présent contrat et à coordonner son intervention avec les autres corps d'état.",
        "delais_penalites": "5.3 — Pénalités de retard",
        "delais_penalites_text": "En cas de retard non justifié par un cas de force majeure (art. 268 et 269 du D.O.C.), des pénalités de retard seront appliquées d'office, sans mise en demeure préalable, à raison de {taux}‰ (pour mille) du montant HT du marché par jour calendaire de retard, plafonnées à {plafond}% du montant total du marché.",
        "delais_resiliation": "5.4 — Résiliation pour dépassement",
        "delais_resiliation_text": "Au-delà du plafond de pénalités, l'Entrepreneur Principal se réserve le droit de résilier le contrat aux torts exclusifs du Sous-Traitant, sans préjudice de son droit à indemnisation du préjudice subi.",
        # Article 6 – Obligations ST
        "art_obligations_st": "OBLIGATIONS DU SOUS-TRAITANT",
        "oblig_generales": "6.1 — Obligations générales",
        "oblig_generales_list": [
            "Exécuter les travaux conformément aux règles de l'art, aux normes en vigueur et aux documents contractuels",
            "Fournir l'ensemble de la main-d'œuvre qualifiée, des matériaux, outillages et équipements nécessaires",
            "Se conformer au règlement intérieur du chantier et aux consignes de sécurité",
            "Maintenir en permanence un responsable qualifié sur le chantier",
            "Signaler immédiatement toute anomalie, erreur dans les plans ou vice de conception constaté",
            "Assurer le nettoyage quotidien de sa zone de travail et l'évacuation de ses gravats",
            "Respecter la législation du travail, notamment les articles 86 à 91 du Code du Travail marocain relatifs à la sous-entreprise",
            "Être en règle avec les organismes sociaux (CNSS) et fiscaux",
            "Fournir mensuellement les copies des bordereaux de déclaration CNSS de son personnel affecté au chantier",
        ],
        "oblig_specifiques": "6.2 — Obligations spécifiques au lot",
        # Article 7 – Obligations EP
        "art_obligations_ep": "OBLIGATIONS DE L'ENTREPRENEUR PRINCIPAL",
        "oblig_ep_list": [
            "Mettre à disposition du Sous-Traitant les plans, documents techniques et informations nécessaires",
            "Assurer la coordination générale du chantier entre les différents corps d'état",
            "Permettre l'accès au chantier selon le planning convenu",
            "Procéder au paiement dans les délais contractuels",
            "Désigner un interlocuteur unique pour le suivi du lot",
            "Informer le Maître d'Ouvrage de l'intervention du Sous-Traitant conformément à la loi",
            "Mettre à disposition les locaux de stockage si disponibles et les accès nécessaires",
        ],
        # Article 8 – Assurances
        "art_assurances": "ASSURANCES",
        "assurances_intro": "Le Sous-Traitant s'engage à souscrire et maintenir en vigueur pendant toute la durée des travaux et pendant la période de garantie les assurances suivantes :",
        "assurances_rules": [
            "Les attestations d'assurance devront être remises à l'Entrepreneur Principal avant tout début d'exécution.",
            "Le montant de la couverture RC Professionnelle ne pourra être inférieur au montant du présent marché.",
            "Le Sous-Traitant s'engage à informer immédiatement l'Entrepreneur Principal de toute modification, suspension ou résiliation de ses polices d'assurance.",
            "Le défaut d'assurance constitue un motif de résiliation immédiate du contrat aux torts du Sous-Traitant.",
        ],
        "assurances_trc": "L'Entrepreneur Principal déclare avoir souscrit une Assurance Tous Risques Chantier (TRC). Le Sous-Traitant devra se conformer aux conditions de cette police et déclarer tout sinistre dans un délai de 24 heures.",
        # Article 9 – Réception
        "art_reception": "RÉCEPTION DES TRAVAUX",
        "reception_provisoire": "9.1 — Réception provisoire",
        "reception_provisoire_text": "À l'achèvement des travaux, une réception provisoire sera prononcée contradictoirement.",
        "reception_pv_text": "Un procès-verbal sera dressé, avec ou sans réserves.",
        "reception_reserves": "9.2 — Levée des réserves",
        "reception_reserves_text": "Le Sous-Traitant dispose d'un délai de {days} jours pour lever les réserves formulées. Passé ce délai, l'EP pourra faire exécuter les travaux de reprise aux frais du Sous-Traitant.",
        "reception_definitive": "9.3 — Réception définitive",
        "reception_definitive_text": "La réception définitive est prononcée à l'expiration du délai de garantie de {months} mois, après constatation de la levée de toutes les réserves et du bon comportement des ouvrages.",
        "reception_decennale": "9.4 — Garantie décennale",
        "reception_decennale_text": "Conformément aux articles 769 et 770 du D.O.C., le Sous-Traitant reste tenu de la garantie décennale pour les ouvrages relevant de sa responsabilité, lorsque celle-ci est applicable au lot concerné.",
        # Article 10 – Responsabilité
        "art_responsabilite": "RESPONSABILITÉ ET GARANTIES",
        "resp_resultat": "10.1 — Le Sous-Traitant est tenu d'une obligation de résultat quant à la conformité des travaux aux documents contractuels et aux règles de l'art (art. 723 et suivants du D.O.C.).",
        "resp_recours": "10.2 — Le Sous-Traitant garantit l'Entrepreneur Principal contre tout recours de tiers, y compris le Maître d'Ouvrage, pour les dommages résultant de l'exécution défaillante de ses travaux.",
        "resp_personnel": "10.3 — Le Sous-Traitant est seul responsable de son personnel, sous-traitants éventuels et fournisseurs. Il s'engage à respecter la législation du travail et la couverture sociale de ses employés.",
        "resp_defaillance": "10.4 — En cas de défaillance du Sous-Traitant, l'Entrepreneur Principal pourra, après mise en demeure restée infructueuse pendant {days} jours, faire exécuter les travaux par un tiers aux frais et risques du Sous-Traitant, sans préjudice de dommages et intérêts.",
        # Article 11 – Résiliation
        "art_resiliation": "RÉSILIATION",
        "resil_faute": "11.1 — Résiliation pour faute",
        "resil_faute_intro": "Le contrat pourra être résilié de plein droit par l'Entrepreneur Principal en cas de :",
        "resil_faute_list": [
            "Abandon de chantier ou interruption injustifiée des travaux pendant plus de 5 jours ouvrables",
            "Non-respect répété des règles de sécurité sur le chantier",
            "Défaut d'assurance ou de couverture CNSS",
            "Malfaçons graves constatées et non corrigées après mise en demeure",
            "Dépassement du plafond des pénalités de retard",
            "Procédure collective (redressement ou liquidation judiciaire) du Sous-Traitant",
            "Cession du contrat ou sous-traitance non autorisée",
        ],
        "resil_faute_effet": "La résiliation prendra effet {days} jours après l'envoi d'une mise en demeure par lettre recommandée avec accusé de réception restée sans effet.",
        "resil_convenance": "11.2 — Résiliation pour convenance",
        "resil_convenance_text": "L'Entrepreneur Principal se réserve le droit de résilier le contrat pour convenance moyennant un préavis de 15 jours et le paiement des travaux régulièrement exécutés et réceptionnés.",
        "resil_consequences": "11.3 — Conséquences",
        "resil_consequences_text": "En cas de résiliation pour faute, un état contradictoire des travaux sera dressé. Le Sous-Traitant ne pourra prétendre à aucune indemnité et devra supporter les surcoûts de reprise par un tiers.",
        # Article 12 – HSE
        "art_hse": "HYGIÈNE, SÉCURITÉ ET ENVIRONNEMENT",
        "hse_list": [
            "12.1 — Le Sous-Traitant s'engage à respecter toutes les dispositions légales et réglementaires en matière d'hygiène et de sécurité du travail, notamment les dispositions du Code du Travail marocain (Titre IV, Livre II).",
            "12.2 — Le Sous-Traitant est responsable de la fourniture des Équipements de Protection Individuelle (ÉPI) à son personnel.",
            "12.3 — Le Sous-Traitant s'engage à ne pas employer de mineurs et à respecter les horaires de travail légaux.",
            "12.4 — En cas d'accident du travail sur le chantier impliquant le personnel du Sous-Traitant, ce dernier assume l'entière responsabilité et en informe immédiatement l'Entrepreneur Principal.",
            "12.5 — Le Sous-Traitant désigne un responsable sécurité parmi son personnel affecté au chantier.",
        ],
        # Optional clauses
        "clause_confid": "CONFIDENTIALITÉ",
        "clause_confid_text": "Le Sous-Traitant s'engage à traiter comme strictement confidentielles toutes les informations techniques, commerciales et financières dont il pourrait avoir connaissance dans le cadre de l'exécution du présent contrat. Cette obligation s'étend à son personnel et à tout tiers auquel il pourrait faire appel. Elle survit à l'extinction du contrat pour une durée de 3 ans. Toute violation expose le Sous-Traitant au paiement d'une indemnité forfaitaire de 20% du montant HT du marché, sans préjudice du droit de l'Entrepreneur Principal à demander réparation du préjudice réel subi.",
        "clause_non_conc": "NON-CONCURRENCE",
        "clause_non_conc_text": "Le Sous-Traitant s'interdit, pendant toute la durée du contrat et pendant une période de 12 mois suivant son terme, de contracter directement avec le Maître d'Ouvrage ou avec tout acquéreur des lots du projet, pour des prestations similaires à celles objet du présent contrat, dans un rayon de 20 km autour du projet. Toute violation expose le Sous-Traitant au paiement d'une indemnité forfaitaire de 30% du montant HT du présent contrat.",
        "clause_non_deb": "NON-DÉBAUCHAGE",
        "clause_non_deb_text": "Chacune des Parties s'interdit de recruter ou de tenter de recruter, directement ou indirectement, tout salarié ou collaborateur de l'autre Partie ayant participé à l'exécution du présent contrat, pendant toute la durée du contrat et pendant une période de 12 mois suivant son terme. Toute violation entraînera le paiement d'une indemnité forfaitaire équivalente à 12 mois de rémunération brute du salarié concerné.",
        "clause_cascade": "INTERDICTION DE SOUS-TRAITANCE EN CASCADE",
        "clause_cascade_text": "Le Sous-Traitant s'interdit formellement de sous-traiter tout ou partie des travaux objets du présent contrat à un tiers, sauf accord écrit et préalable de l'Entrepreneur Principal. En cas de violation, l'Entrepreneur Principal pourra résilier immédiatement le contrat aux torts exclusifs du Sous-Traitant, sans mise en demeure préalable, et sans préjudice de dommages et intérêts.",
        "clause_enviro": "CLAUSE ENVIRONNEMENTALE",
        "clause_enviro_text": "Le Sous-Traitant s'engage à respecter la législation environnementale en vigueur au Maroc, notamment la loi n° 11-03 relative à la protection et à la mise en valeur de l'environnement. Il s'engage à gérer ses déchets de chantier de manière responsable et à les évacuer vers les décharges autorisées, à limiter les nuisances sonores et les émissions de poussière, à utiliser des matériaux respectueux de l'environnement dans la mesure du possible et à respecter les horaires de chantier pour limiter les nuisances au voisinage.",
        "clause_pi": "PROPRIÉTÉ INTELLECTUELLE",
        "clause_pi_text": "Tous les plans, études, documents techniques et méthodes développés ou utilisés par le Sous-Traitant dans le cadre du présent contrat et financés par l'Entrepreneur Principal deviennent la propriété exclusive de ce dernier. Le Sous-Traitant ne pourra les utiliser, les reproduire ou les communiquer à des tiers sans l'accord écrit et préalable de l'Entrepreneur Principal.",
        "clause_exclus": "EXCLUSIVITÉ",
        "clause_exclus_text": "Pendant toute la durée d'exécution du présent contrat, le Sous-Traitant s'engage à accorder la priorité aux travaux objet du présent contrat et à ne pas accepter de chantier concurrent susceptible d'affecter sa capacité d'exécution ou de retarder le planning convenu.",
        "clause_revision": "RÉVISION DE PRIX",
        "clause_revision_text": "Par dérogation au caractère ferme du prix, en cas de variation exceptionnelle du coût des matériaux de construction supérieure à 15% par rapport aux prix en vigueur à la date de signature du contrat, les Parties conviennent de se rencontrer pour négocier de bonne foi un ajustement du prix. Cette révision ne pourra intervenir qu'une seule fois et devra être formalisée par avenant signé des deux Parties.",
        # Trailing articles
        "art_litiges": "RÈGLEMENT DES LITIGES",
        "litiges_mediation": "En cas de différend relatif à l'interprétation ou à l'exécution du présent contrat, les Parties s'engagent à soumettre leur litige à une procédure de médiation préalable d'une durée maximale de 30 jours, avant toute saisine des juridictions compétentes.",
        "litiges_tribunal": "À défaut d'accord amiable, tout litige sera soumis à la compétence exclusive du Tribunal de Commerce de Tanger, conformément aux dispositions du Code de Procédure Civile marocain.",
        "litiges_tribunal_mediation": "À défaut d'accord amiable ou de médiation aboutie, tout litige sera soumis à la compétence exclusive du Tribunal de Commerce de Tanger, conformément aux dispositions du Code de Procédure Civile marocain.",
        "art_force_majeure": "FORCE MAJEURE",
        "force_majeure_text": (
            "Conformément aux articles 268 et 269 du D.O.C., aucune des Parties ne sera tenue responsable "
            "d'un manquement à ses obligations contractuelles si ce manquement résulte d'un cas de force majeure, "
            "défini comme un événement imprévisible, irrésistible et extérieur à la volonté des Parties. "
            "La Partie invoquant la force majeure devra en informer l'autre Partie par écrit dans un délai maximum de 5 jours "
            "suivant la survenance de l'événement, en fournissant les justificatifs nécessaires. Les délais contractuels "
            "seront prorogés d'une durée égale à celle de l'empêchement. Si la force majeure persiste "
            "au-delà de 90 jours, chacune des Parties pourra résilier le contrat sans indemnité, sous réserve du paiement des travaux réalisés."
        ),
        "art_dispositions": "DISPOSITIONS GÉNÉRALES ET FINALES",
        "dispositions_items": [
            "Droit applicable : Le présent contrat est régi par le droit marocain, notamment le Dahir formant Code des Obligations et des Contrats (D.O.C.) et le Code de Commerce.",
            "Intégralité : Le présent contrat, ses annexes et les documents contractuels visés à l'Article 3 constituent l'intégralité de l'accord entre les Parties et remplacent tout accord antérieur, écrit ou verbal.",
            "Modification : Toute modification devra faire l'objet d'un avenant écrit signé par les deux Parties.",
            "Nullité partielle : Si l'une des clauses était déclarée nulle ou inapplicable, les autres clauses conserveraient leur pleine validité.",
            "Notifications : Toute notification sera faite par lettre recommandée avec accusé de réception aux adresses des sièges sociaux respectifs. En cas de changement d'adresse, la Partie concernée devra en informer l'autre par écrit dans un délai de 15 jours.",
            "Élection de domicile : Pour l'exécution du présent contrat, les Parties élisent domicile à leurs sièges sociaux respectifs.",
        ],
        # Annexe
        "annexe_title": "ANNEXES — LISTE DES PIÈCES JOINTES",
        "annexe_items": [
            "Devis descriptif et quantitatif du Sous-Traitant",
            "Planning d'exécution détaillé",
            "Attestation d'assurance RC Professionnelle",
            "Attestation d'affiliation CNSS",
            "Copie du Registre de Commerce",
            "Copie de la CIN du représentant légal",
            "Attestation de régularité fiscale",
            "RIB du Sous-Traitant",
            "Plans d'exécution visés BPE (lot concerné)",
            "CCTP du lot",
            "Caution de bonne exécution (si applicable)",
            "Attestation de garantie décennale (si applicable)",
        ],
        "annexe_col_no": "N°",
        "annexe_col_doc": "Document",
        "annexe_col_status": "Remis",
        "annexe_status_blank": "☐ Oui ☐ Non",
        "special_clauses_title": "CLAUSES PARTICULIÈRES",
    },
    "en": {
        "contrat_title": "SUBCONTRACTING AGREEMENT",
        "preamble": (
            "Drawn up in application of the provisions of the Dahir of 12 August 1913 "
            "forming the Code of Obligations and Contracts (D.O.C.) and Articles 86 to 91 "
            "of the Moroccan Labour Code"
        ),
        "entre": "BETWEEN THE UNDERSIGNED:",
        "lbl_ep": "THE PRINCIPAL CONTRACTOR",
        "lbl_st": "THE SUBCONTRACTOR",
        "ci_ep": 'Hereinafter referred to as "The Principal Contractor" or "PC"',
        "ci_st": 'Hereinafter referred to as "The Subcontractor" or "SC"',
        "parties_ensemble": "Hereinafter jointly referred to as 'The Parties'.",
        "et": "AND",
        "fait_a": "Done in",
        "le": "on",
        "en_exemplaires": "in two (2) original copies, one for each party.",
        "lu_approuve": "Read and approved — Signature and stamp",
        "paraphes": "Each page of this contract must be initialled by both Parties. Annexes are an integral part of the contract.",
        "page_x_sur_y": "Page {page} of {pages}",
        "projet": "Project",
        "ref": "Ref.",
        "date_label": "Date:",
        # Article 1
        "art_parties": "CONTRACTING PARTIES",
        "partie_ep_title": "1.1 — The Principal Contractor",
        "partie_st_title": "1.2 — The Subcontractor",
        "raison_sociale": "Company name",
        "forme_juridique": "Legal form",
        "capital_social": "Share capital",
        "rc": "Trade Register",
        "ice": "ICE",
        "if_label": "Tax ID",
        "cnss": "CNSS",
        "siege": "Registered office",
        "representant": "Legal representative",
        "qualite": "Position",
        "cin": "ID Card",
        "telephone": "Phone",
        "email": "Email",
        "rib": "Bank Account",
        "banque": "Bank",
        # Article 2
        "art_objet": "PURPOSE OF THE CONTRACT",
        "objet_intro": (
            "This contract aims to entrust the Subcontractor, under the responsibility of the Principal Contractor "
            "and in accordance with Article 723 et seq. of the D.O.C. relating to contracts for work, "
            "with the execution of the following works:"
        ),
        "objet_projet": "Project:",
        "objet_adresse": "Address:",
        "objet_mo": "Client/Owner:",
        "objet_permis": "Building permit no.:",
        "objet_normes": "Applicable standards:",
        "objet_declaration": "The Subcontractor declares having familiarised itself with all project documents, execution plans and technical specifications, and accepts them without reservation.",
        # Article 3
        "art_docs": "CONTRACTUAL DOCUMENTS",
        "docs_intro": "The contractual documents are, in descending order of priority:",
        "docs_list": [
            "This contract and its annexes",
            "The Technical Specifications (CCTP) for the trade",
            "The Administrative Conditions (CCAP)",
            'The execution plans marked "Approved For Execution" (BPE)',
            "The Subcontractor's descriptive and quantitative quotation",
            "The general execution schedule",
            "Applicable standards and regulations",
            "Rules of the trade and DTU standards applicable to the trade",
        ],
        "docs_contradiction": "In the event of a conflict between documents, the order of priority above shall prevail.",
        # Article 4
        "art_prix": "PRICE AND FINANCIAL CONDITIONS",
        "prix_montant": "4.1 — Contract amount",
        "prix_type": "Price type:",
        "prix_comprend": "This price includes all supplies, labour, transport, insurance, plant and equipment, overheads, profit and all ancillary costs necessary for the proper execution of the works.",
        "prix_ht": "Amount excl. tax (HT):",
        "prix_tva": "VAT ({tva}%):",
        "prix_ttc": "Amount incl. tax (TTC):",
        "prix_arrete": "Fixed at the sum of:",
        "prix_modalites": "4.2 — Payment terms",
        "prix_virement_intro": "Payment shall be made by bank transfer{rib_info} according to the schedule below:",
        "prix_delai_paiement": "Each progress claim shall be submitted in three (3) copies, accompanied by signed attachments. The payment period is set at {days} days from receipt of the compliant invoice, in accordance with commercial practices and Article 78 of the Moroccan Commercial Code.",
        "prix_avance": "4.3 — Advance payment",
        "prix_avance_text": "An advance payment of {pct}% of the amount excl. tax, i.e. {amount}, shall be paid to the Subcontractor upon signing the contract, upon presentation of an advance repayment guarantee issued by a bank accredited in Morocco. This advance shall be deducted proportionally from each progress claim.",
        "prix_retenue": "4.4 — Retention money",
        "prix_retenue_text": "A retention of {pct}% shall be withheld from each progress claim. It shall be released upon expiry of the {months}-month warranty period, less any outstanding defects. The Subcontractor may substitute this retention with a bank guarantee of the same amount issued by an accredited credit institution in Morocco.",
        "prix_supplementaires": "4.5 — Additional works",
        "prix_supplementaires_text": "No additional service may be invoiced without a written service order previously signed by the Principal Contractor. Any work carried out without prior written agreement shall not give rise to any additional remuneration.",
        # Article 5
        "art_delais": "EXECUTION DEADLINES",
        "delais_global": "5.1 — Overall deadline",
        "delais_global_text": "The overall deadline for execution of the works is set at {val} {unit} from the date of notification of the commencement service order.",
        "delais_planning": "5.2 — Schedule",
        "delais_planning_text": "The Subcontractor undertakes to comply with the detailed schedule annexed to this contract and to coordinate its works with the other trades on site.",
        "delais_penalites": "5.3 — Delay penalties",
        "delais_penalites_text": "In the event of delay not justified by a force majeure event (Articles 268 and 269 of the D.O.C.), delay penalties shall apply automatically, without prior formal notice, at a rate of {taux}‰ (per mille) of the HT contract amount per calendar day of delay, capped at {plafond}% of the total contract amount.",
        "delais_resiliation": "5.4 — Termination for exceeding cap",
        "delais_resiliation_text": "Beyond the penalty cap, the Principal Contractor reserves the right to terminate the contract at the sole fault of the Subcontractor, without prejudice to its right to claim compensation for actual loss suffered.",
        # Article 6
        "art_obligations_st": "SUBCONTRACTOR'S OBLIGATIONS",
        "oblig_generales": "6.1 — General obligations",
        "oblig_generales_list": [
            "Execute works in accordance with the rules of the trade, applicable standards and contractual documents",
            "Provide all qualified labour, materials, tools and equipment required",
            "Comply with the site rules and safety instructions",
            "Maintain a qualified supervisor on site at all times",
            "Immediately report any anomaly, error in plans or design defect discovered",
            "Ensure daily cleaning of the work area and removal of rubble",
            "Comply with labour legislation, particularly Articles 86 to 91 of the Moroccan Labour Code relating to subcontracting",
            "Be up to date with social (CNSS) and tax obligations",
            "Provide monthly copies of CNSS declaration forms for personnel assigned to the site",
        ],
        "oblig_specifiques": "6.2 — Trade-specific obligations",
        # Article 7
        "art_obligations_ep": "PRINCIPAL CONTRACTOR'S OBLIGATIONS",
        "oblig_ep_list": [
            "Make available to the Subcontractor the plans, technical documents and information required",
            "Ensure overall coordination of the site between the various trades",
            "Allow access to the site in accordance with the agreed schedule",
            "Make payment within contractual deadlines",
            "Designate a single point of contact for trade monitoring",
            "Inform the Client/Owner of the Subcontractor's intervention in accordance with the law",
            "Make available storage space if available and the necessary access",
        ],
        # Article 8
        "art_assurances": "INSURANCE",
        "assurances_intro": "The Subcontractor undertakes to take out and maintain throughout the works and during the warranty period the following insurance:",
        "assurances_rules": [
            "Insurance certificates must be remitted to the Principal Contractor before any commencement of works.",
            "The amount of Professional Liability Insurance cover shall not be less than the value of this contract.",
            "The Subcontractor undertakes to immediately inform the Principal Contractor of any modification, suspension or cancellation of its insurance policies.",
            "Lack of insurance cover shall constitute grounds for immediate termination of the contract at the sole fault of the Subcontractor.",
        ],
        "assurances_trc": "The Principal Contractor declares having taken out an All-Risk Builders' Insurance (TRC). The Subcontractor must comply with the conditions of this policy and report any claim within 24 hours.",
        # Article 9
        "art_reception": "ACCEPTANCE OF WORKS",
        "reception_provisoire": "9.1 — Provisional acceptance",
        "reception_provisoire_text": "Upon completion of the works, provisional acceptance shall be pronounced jointly.",
        "reception_pv_text": "Minutes shall be drawn up, with or without reservations.",
        "reception_reserves": "9.2 — Defects remediation",
        "reception_reserves_text": "The Subcontractor has {days} days to remedy the defects noted. After this period, the PC may have the remedial works carried out at the Subcontractor's expense.",
        "reception_definitive": "9.3 — Final acceptance",
        "reception_definitive_text": "Final acceptance is pronounced at the expiry of the {months}-month warranty period, after verification that all defects have been remedied and the works are performing satisfactorily.",
        "reception_decennale": "9.4 — Ten-year warranty",
        "reception_decennale_text": "In accordance with Articles 769 and 770 of the D.O.C., the Subcontractor remains bound by the ten-year warranty for works falling within its responsibility, where applicable to the relevant trade.",
        # Article 10
        "art_responsabilite": "LIABILITY AND WARRANTIES",
        "resp_resultat": "10.1 — The Subcontractor is bound by an obligation of result regarding the conformity of the works with the contractual documents and rules of the trade (Articles 723 et seq. of the D.O.C.).",
        "resp_recours": "10.2 — The Subcontractor shall indemnify the Principal Contractor against any third-party claim, including from the Client/Owner, for damages resulting from defective execution of its works.",
        "resp_personnel": "10.3 — The Subcontractor is solely responsible for its personnel, any sub-subcontractors and suppliers. It undertakes to comply with labour legislation and social security coverage for its employees.",
        "resp_defaillance": "10.4 — In the event of the Subcontractor's failure, the Principal Contractor may, after a formal notice that has remained without effect for {days} days, have the works carried out by a third party at the Subcontractor's expense and risk, without prejudice to damages.",
        # Article 11
        "art_resiliation": "TERMINATION",
        "resil_faute": "11.1 — Termination for fault",
        "resil_faute_intro": "The contract may be terminated as of right by the Principal Contractor in the following cases:",
        "resil_faute_list": [
            "Abandonment of the site or unjustified interruption of works for more than 5 working days",
            "Repeated failure to comply with safety rules on site",
            "Lack of insurance or CNSS coverage",
            "Serious defects noted and not corrected after formal notice",
            "Exceeding the contractual penalty cap for delays",
            "Collective proceedings (judicial recovery or liquidation) of the Subcontractor",
            "Assignment of the contract or unauthorised subcontracting",
        ],
        "resil_faute_effet": "Termination shall take effect {days} days after sending a formal notice by registered letter with acknowledgement of receipt that has remained without effect.",
        "resil_convenance": "11.2 — Termination for convenience",
        "resil_convenance_text": "The Principal Contractor reserves the right to terminate the contract for convenience with 15 days' notice and payment of the works regularly executed and accepted.",
        "resil_consequences": "11.3 — Consequences",
        "resil_consequences_text": "In the event of termination for fault, a joint inspection of the works shall be carried out. The Subcontractor may not claim any indemnity and shall bear the additional costs of remediation by a third party.",
        # Article 12
        "art_hse": "HEALTH, SAFETY AND ENVIRONMENT",
        "hse_list": [
            "12.1 — The Subcontractor undertakes to comply with all legal and regulatory provisions relating to occupational health and safety, in particular the provisions of the Moroccan Labour Code (Title IV, Book II).",
            "12.2 — The Subcontractor is responsible for providing Personal Protective Equipment (PPE) to its personnel.",
            "12.3 — The Subcontractor undertakes not to employ minors and to comply with statutory working hours.",
            "12.4 — In the event of a work accident on site involving the Subcontractor's personnel, the Subcontractor assumes full liability and must immediately inform the Principal Contractor.",
            "12.5 — The Subcontractor shall designate a safety officer from among its site personnel.",
        ],
        # Optional clauses
        "clause_confid": "CONFIDENTIALITY",
        "clause_confid_text": "The Subcontractor undertakes to treat as strictly confidential all technical, commercial and financial information that may come to its knowledge in the performance of this contract. This obligation extends to its personnel and to any third party it may engage. It survives the termination of the contract for a period of 3 years. Any breach exposes the Subcontractor to a lump-sum indemnity equal to 20% of the pre-tax contract amount, without prejudice to the Principal Contractor's right to claim compensation for the actual loss suffered.",
        "clause_non_conc": "NON-COMPETITION",
        "clause_non_conc_text": "The Subcontractor undertakes, throughout the term of the contract and for a period of 12 months after its expiry, not to contract directly with the Employer or with any purchaser of lots in the project for services similar to those covered by this contract, within a radius of 20 km around the project. Any breach exposes the Subcontractor to a lump-sum indemnity equal to 30% of the pre-tax amount of this contract.",
        "clause_non_deb": "NON-SOLICITATION",
        "clause_non_deb_text": "Each Party undertakes not to recruit or attempt to recruit, directly or indirectly, any employee or collaborator of the other Party who has been involved in the performance of this contract, during the contract and for a period of 12 months after its termination. In the event of breach, a lump-sum indemnity equal to 12 months' gross salary of the person concerned shall be due.",
        "clause_cascade": "PROHIBITION OF CASCADE SUBCONTRACTING",
        "clause_cascade_text": "The Subcontractor is formally prohibited from subcontracting all or part of the works covered by this contract to a third party unless it has obtained the Principal Contractor's prior written consent. In the event of breach, the Principal Contractor may terminate the contract immediately at the Subcontractor's sole fault, without prior notice and without prejudice to damages.",
        "clause_enviro": "ENVIRONMENTAL CLAUSE",
        "clause_enviro_text": "The Subcontractor undertakes to comply with environmental legislation in force in Morocco, in particular Law No. 11-03 on environmental protection and enhancement. It undertakes to manage site waste responsibly and remove it to authorised dumps, to limit noise nuisance and dust emissions, to use environmentally friendly materials where possible and to respect site working hours in order to limit disturbance to neighbouring properties.",
        "clause_pi": "INTELLECTUAL PROPERTY",
        "clause_pi_text": "All plans, studies, technical documents and methods developed or used by the Subcontractor in the course of this contract and financed by the Principal Contractor shall become the exclusive property of the latter. The Subcontractor may not use, reproduce or communicate them to third parties without the Principal Contractor's prior written consent.",
        "clause_exclus": "EXCLUSIVITY",
        "clause_exclus_text": "Throughout the performance of this contract, the Subcontractor undertakes to give priority to the works covered by this contract and not to accept any competing site likely to affect its execution capacity or delay the agreed schedule.",
        "clause_revision": "PRICE REVISION",
        "clause_revision_text": "By way of derogation from the fixed-price nature of the contract, in the event of an exceptional variation in the cost of construction materials greater than 15% compared with the prices in force on the signing date, the Parties agree to meet and negotiate in good faith an adjustment to the price. This revision may occur only once and must be formalised by an amendment signed by both Parties.",
        # Trailing articles
        "art_litiges": "DISPUTE RESOLUTION",
        "litiges_mediation": "In the event of a dispute relating to the interpretation or performance of this contract, the Parties undertake to submit their dispute to a prior mediation procedure lasting a maximum of 30 days, before any referral to the competent courts.",
        "litiges_tribunal": "Failing amicable agreement, any dispute shall be subject to the exclusive jurisdiction of the Commercial Court of Tangier, in accordance with the provisions of the Moroccan Code of Civil Procedure.",
        "litiges_tribunal_mediation": "Failing amicable agreement or successful mediation, any dispute shall be subject to the exclusive jurisdiction of the Commercial Court of Tangier, in accordance with the provisions of the Moroccan Code of Civil Procedure.",
        "art_force_majeure": "FORCE MAJEURE",
        "force_majeure_text": (
            "In accordance with Articles 268 and 269 of the D.O.C., neither of the Parties shall be held liable "
            "for a failure to fulfil its contractual obligations if such failure results from a force majeure event, "
            "defined as an unforeseeable, irresistible event beyond the control of the Parties. "
            "The Party invoking force majeure must inform the other Party in writing within a maximum of 5 days "
            "following the occurrence of the event, providing the necessary supporting documents. Contractual deadlines "
            "shall be extended by a period equal to that of the impediment. If the force majeure event persists "
            "beyond 90 days, each of the Parties may terminate the contract without compensation, subject to payment for works already carried out."
        ),
        "art_dispositions": "GENERAL AND FINAL PROVISIONS",
        "dispositions_items": [
            "Applicable law: This contract is governed by Moroccan law, in particular the Dahir forming the Code of Obligations and Contracts (D.O.C.) and the Commercial Code.",
            "Entire agreement: This contract, its annexes and the contractual documents referred to in Article 3 constitute the entire agreement between the Parties and supersede all prior agreements, written or oral.",
            "Amendment: Any modification must be made by a written amendment signed by both Parties.",
            "Severability: If any clause is declared null or unenforceable, the remaining clauses shall retain their full validity.",
            "Notices: All notices shall be sent by registered letter with acknowledgement of receipt to the registered offices of the respective Parties. In the event of a change of address, the Party concerned must inform the other in writing within 15 days.",
            "Elected domicile: For the performance of this contract, the Parties elect domicile at their respective registered offices.",
        ],
        # Annexe
        "annexe_title": "ANNEXES — LIST OF ATTACHED DOCUMENTS",
        "annexe_items": [
            "Subcontractor's descriptive and quantitative quotation",
            "Detailed execution schedule",
            "Professional Liability Insurance certificate",
            "CNSS registration certificate",
            "Copy of Trade Register",
            "Copy of legal representative's ID card",
            "Tax clearance certificate",
            "Subcontractor's bank account details (RIB)",
            "BPE-approved execution plans (relevant trade)",
            "CCTP for the trade",
            "Performance bond (if applicable)",
            "Ten-year warranty certificate (if applicable)",
        ],
        "annexe_col_no": "No.",
        "annexe_col_doc": "Document",
        "annexe_col_status": "Provided",
        "annexe_status_blank": "☐ Yes ☐ No",
        "special_clauses_title": "SPECIAL CLAUSES",
    },
}


def st_t(key: str, lang: str = "fr") -> str:
    """Return translated text for *key* in *lang*."""
    return ST_TX.get(lang, ST_TX["fr"]).get(key, ST_TX["fr"].get(key, key))
