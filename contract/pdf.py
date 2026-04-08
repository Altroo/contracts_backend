"""
contract/pdf.py
~~~~~~~~~~~~~~~
Generates a full legal contract PDF using WeasyPrint + inline HTML/CSS,
replicating the output of casa_di_lusso_contracts_v2.html.
Supports both French (fr) and English (en) via the *lang* parameter.
"""

# i18n: skip-file — bilingual document generator; FR+EN content is intentional

from django.http import HttpResponse

from .i18n import (
    TYPELABEL,
    CTYPES_DISPLAY,
    TYPE_BIEN_LABELS,
    MODE_NAMES,
    CONFID_LABELS,
    QUALITE_LABELS,
    GARANTIE_LABELS,
)


def _fmt_date(d):
    """Return a formatted date string like '27 / 02 / 2026'."""
    if not d:
        return "…… / …… / ………"
    if hasattr(d, "strftime"):
        return d.strftime("%d / %m / %Y")
    return str(d)


def _fmt_amt(n, dev="MAD"):
    """Return a French-formatted amount string like '1 234,56 MAD'."""
    try:
        val = float(n)
    except (TypeError, ValueError):
        val = 0.0
    raw = f"{val:,.2f}"
    whole, dec = raw.split(".")
    whole = whole.replace(",", "\u202f")
    return f"{whole},{dec}\u00a0{dev}"


def _format_penalite_retard(c, lang: str) -> str:
    unite = getattr(c, "penalite_retard_unite", "mad_per_day") or "mad_per_day"
    penalite = float(c.penalite_retard or 1.5)
    if unite == "percent_per_day":
        return f"{penalite:g}% par jour" if lang == "fr" else f"{penalite:g}% per day"
    return f"{penalite:g} MAD par jour" if lang == "fr" else f"{penalite:g} MAD per day"


def _esc(text: str) -> str:
    """Minimal HTML escaping of a plain-text string."""
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── backward-compatible aliases (doc.py imports these names) ──────────────────
_TYPELABEL = TYPELABEL["fr"]
_CTYPES_DISPLAY = CTYPES_DISPLAY["fr"]
_TYPE_BIEN_LABELS = TYPE_BIEN_LABELS["fr"]
_MODE_NAMES = MODE_NAMES["fr"]
_CONFID_LABELS = CONFID_LABELS
_QUALITE_LABELS = QUALITE_LABELS["fr"]


def _is_societe(qualite: str) -> bool:
    if not qualite:
        return False
    q = qualite.lower()
    return "societe" in q or "morale" in q or "soci\u00e9t\u00e9" in q


_PDF_CSS_TMPL = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

@page {
  size: A4;
  margin: 18mm 18mm 22mm 18mm;
  @bottom-center {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 7pt;
    color: #ccc;
    content: "Page " counter(page) " __PAGE_SEP__ " counter(pages);
  }
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Inter', Arial, Helvetica, sans-serif;
  font-size: 9pt;
  color: #1C1C2E;
  background: #fff;
  line-height: 1.75;
}

/* ── top strip ── */
.c-topstrip {
  height: 4px;
  background: linear-gradient(90deg, #0F0F1A 0%, #B8973A 50%, #0F0F1A 100%);
  margin-bottom: 20pt;
}

/* ── header ── */
.c-header {
  display: table; width: 100%;
  padding-bottom: 14pt;
  border-bottom: 0.5pt solid #E2D9C8;
  margin-bottom: 16pt;
}
.c-header-left  { display: table-cell; vertical-align: top; }
.c-header-right { display: table-cell; vertical-align: top; text-align: right; }
.c-logo {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 20pt; font-weight: 700; letter-spacing: 2px;
  color: #0F0F1A; line-height: 1;
}
.cg { color: #B8973A; }
.c-logo-tag { font-size: 7.5pt; color: #999; letter-spacing: 2px; text-transform: uppercase; margin-top: 3pt; }
.c-logo-info { font-size: 7pt; color: #bbb; line-height: 1.8; margin-top: 5pt; }
.c-ref {
  font-family: 'JetBrains Mono', 'Courier New', monospace;
  background: #0F0F1A; color: #B8973A;
  padding: 3pt 9pt; font-size: 9pt; font-weight: 600;
  letter-spacing: 1px; display: inline-block; margin-bottom: 6pt;
  border-radius: 3pt;
}
.c-date { font-size: 8pt; color: #888; line-height: 1.9; }
.c-date strong { color: #1C1C2E; font-weight: 600; }

/* ── confidential ribbon ── */
.c-confidential {
  text-align: center; font-size: 7pt; letter-spacing: 3px;
  text-transform: uppercase; color: #ccc; font-weight: 600;
  margin-bottom: 14pt;
}
.c-confidential span {
  border: 0.5pt solid #ddd; padding: 2pt 10pt; border-radius: 8pt;
}

/* ── title block ── */
.c-title {
  text-align: center; margin: 0 0 16pt;
  padding: 14pt 0 12pt;
  border-top: 1pt solid #eee; border-bottom: 1pt solid #eee;
  position: relative;
}
.c-title::before {
  content: '';
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 40pt; height: 3pt; background: #B8973A;
  border-radius: 0 0 2pt 2pt;
}
.c-title h1 {
  font-family: 'Cormorant Garamond', Georgia, serif;
  font-size: 14pt; font-weight: 700; text-transform: uppercase;
  letter-spacing: 2px; color: #0F0F1A; margin-bottom: 4pt;
}
.c-subtitle { font-size: 8pt; color: #aaa; letter-spacing: 1.5px; text-transform: uppercase; }
.c-type-badge {
  display: inline-block; margin-top: 6pt;
  background: #F7F0E0; border: 1pt solid #B8973A; color: #B8973A;
  padding: 2pt 10pt; font-size: 7.5pt; font-weight: 700;
  letter-spacing: 1.5px; text-transform: uppercase; border-radius: 10pt;
}

/* ── parties ── */
.c-between { font-size: 9pt; font-weight: 600; color: #666; margin-bottom: 8pt; font-style: italic; }
.c-parties { display: table; width: 100%; margin-bottom: 16pt; border-spacing: 8pt 0; }
.c-party {
  display: table-cell; width: 50%; padding: 10pt 12pt;
  vertical-align: top; font-size: 8.5pt; line-height: 1.85;
}
.c-party.prest { background: #0F0F1A; color: rgba(255,255,255,0.85); border-radius: 4pt; }
.c-party.client { background: #FAF6EC; border: 1pt solid #B8973A; border-radius: 4pt; }
.c-party-label {
  font-size: 7pt; font-weight: 700; letter-spacing: 2px;
  text-transform: uppercase; color: #B8973A;
  padding-bottom: 5pt; margin-bottom: 6pt;
}
.c-party.prest .c-party-label { border-bottom: 0.5pt solid rgba(184,151,58,0.3); }
.c-party.client .c-party-label { border-bottom: 0.5pt solid #B8973A; }
.c-party.prest strong { color: #fff; }
.c-party.client strong { color: #0F0F1A; }
.c-party em { font-size: 8pt; opacity: 0.7; font-style: italic; }

/* ── services ── */
.c-services-box { background: #F9F5EC; border: 1pt solid #EDE8DA; padding: 8pt 11pt; margin: 7pt 0; border-radius: 4pt; }
.c-services-title { font-size: 7pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #B8973A; margin-bottom: 5pt; }
.c-stags { display: flex; flex-wrap: wrap; gap: 5px; }
.c-stag { background: #0F0F1A; color: #B8973A; padding: 2px 9px; font-size: 7.5pt; font-weight: 600; display: inline-block; border-radius: 10pt; letter-spacing: 0.3px; }

/* ── articles ── */
.art { margin-bottom: 11pt; page-break-inside: avoid; }
.art-title {
  font-size: 8pt; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1.5px; color: #0F0F1A; background: #F7F0E0;
  border-left: 3pt solid #B8973A; padding: 5pt 10pt 5pt 12pt;
  margin-bottom: 6pt; display: flex; align-items: center; gap: 6px;
  border-radius: 0 4pt 4pt 0;
}
.art-title .anum {
  font-family: 'JetBrains Mono', 'Courier New', monospace; font-size: 8px;
  color: #B8973A; background: #0F0F1A; padding: 3pt 6pt;
  border-radius: 3pt; letter-spacing: 0;
}
.art-body { font-size: 8.5pt; color: #222; padding: 0 4pt; line-height: 1.8; }
.art-body p  { margin-bottom: 4pt; }
.art-body ul { padding-left: 15pt; margin: 3pt 0; }
.art-body ol { padding-left: 15pt; margin: 3pt 0; }
.art-body li { margin-bottom: 2pt; }
.art-body strong { color: #0F0F1A; }
.highlight { background: #F7F0E0; border-left: 2pt solid #B8973A; padding: 5pt 9pt; margin: 5pt 0; font-size: 8pt; border-radius: 0 3pt 3pt 0; }
.warning-box { background: #FDF0EC; border: 1pt solid #f0c4bc; padding: 6pt 9pt; margin: 5pt 0; font-size: 8pt; color: #B5341A; border-radius: 3pt; }
.sub-title { font-size: 8.5pt; font-weight: 700; color: #0F0F1A; margin: 7pt 0 3pt; padding-left: 0; }
.art-divider { height: 1pt; background: #EDE8DA; margin: 7pt 0; }

/* ── planning grid ── */
.plan-grid { display: table; width: 100%; margin: 7pt 0; border-spacing: 6pt 0; }
.plan-card { display: table-cell; width: 33%; background: #F9F5EC; border: 0.5pt solid #EDE8DA; padding: 6pt 9pt; border-radius: 4pt; }
.plan-card-label { font-size: 7pt; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; color: #6B6B80; margin-bottom: 2pt; }
.plan-card-val { font-weight: 600; color: #0F0F1A; font-size: 8.5pt; }

/* ── payment table ── */
.pay-table { width: 100%; border-collapse: collapse; margin: 7pt 0; font-size: 8.5pt; }
.pay-table thead tr { background: #0F0F1A; }
.pay-table th { padding: 5pt 9pt; text-align: left; font-size: 7pt; letter-spacing: 1px; text-transform: uppercase; color: #B8973A; font-weight: 600; }
.pay-table td { padding: 5pt 9pt; border-bottom: 0.5pt solid #E2D9C8; }
.pay-table tr.even td { background: #F9F5EC; }
.pay-table .ptotal td { background: #F7F0E0 !important; font-weight: bold; color: #0F0F1A; }
.pay-table .mono { font-family: 'JetBrains Mono', 'Courier New', monospace; font-weight: 600; font-size: 8pt; }

/* ── signatures ── */
.sigs-box { margin-top: 22pt; border-top: 1pt solid #E2D9C8; padding-top: 14pt; page-break-inside: avoid; }
.sigs-top { display: table; width: 100%; margin-bottom: 12pt; }
.sigs-top-left  { display: table-cell; vertical-align: middle; }
.sigs-top-right { display: table-cell; vertical-align: middle; text-align: right; }
.sigs-title { font-size: 8pt; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #0F0F1A; }
.sigs-date  { font-size: 8pt; color: #888; }
.sigs-grid  { display: table; width: 100%; border-spacing: 10pt 0; }
.sig-box { display: table-cell; width: 50%; border: 1pt solid #E2D9C8; padding: 11pt; min-height: 80pt; vertical-align: top; border-radius: 4pt; }
.sig-label { font-size: 7pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #B8973A; margin-bottom: 3pt; }
.sig-note  { font-size: 8pt; color: #aaa; margin-bottom: 9pt; font-style: italic; }
.sig-line  { border-bottom: 0.5pt dashed #ccc; height: 42pt; margin-bottom: 7pt; }
.sig-name  { font-size: 8.5pt; font-weight: 600; color: #1C1C2E; }
.sig-role  { font-size: 7.5pt; color: #aaa; }

/* ── initials ── */
.initials-row { margin-top: 9pt; border: 1pt solid #EDE8DA; padding: 7pt 11pt; background: #F9F5EC; display: table; width: 100%; font-size: 8pt; color: #888; text-align: center; border-radius: 4pt; }
.init-box    { display: table-cell; width: 22%; text-align: center; vertical-align: middle; }
.init-center { display: table-cell; vertical-align: middle; text-align: center; font-size: 8pt; color: #bbb; padding: 0 8pt; }
.init-line   { width: 65pt; height: 20pt; border-bottom: 0.5pt dashed #ccc; display: inline-block; margin-bottom: 3pt; }
.init-label  { font-size: 7pt; color: #bbb; letter-spacing: 0.5px; }

/* ── footer ── */
.c-footer { margin-top: 14pt; padding-top: 7pt; border-top: 0.5pt solid #E2D9C8; display: table; width: 100%; font-size: 7pt; color: #bbb; }
.c-footer-logo  { display: table-cell; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 10pt; font-weight: 700; color: #B8973A; }
.c-footer-mid   { display: table-cell; text-align: center; }
.c-footer-right { display: table-cell; text-align: right; }
"""


def _build_articles(c, lang="fr") -> list:
    """
    Build all contract articles with bilingual support (fr/en).
    Returns list of dicts: [{'num': '02', 'title': '...', 'body': '...'}, ...]
    """
    fr = lang == "fr"
    articles = []
    _n = [0]

    def _next():
        _n[0] += 1
        return _n[0]

    def _add(title: str, body: str):
        articles.append({"num": str(_next()).zfill(2), "title": title, "body": body})

    type_label = TYPELABEL[lang].get(c.type_contrat or "", c.type_contrat or "")
    type_bien_lbl = TYPE_BIEN_LABELS[lang].get(
        c.type_bien or "autre", c.type_bien or ""
    )
    surface_str = f" \u2013 {c.surface}\u00a0m\u00b2" if c.surface else ""
    services = c.services if isinstance(c.services, list) else []
    clauses = c.clauses_actives if isinstance(c.clauses_actives, list) else []

    stags = "".join(f'<span class="c-stag">{_esc(s)}</span>' for s in services)
    svc_title = "SERVICES CONVENUS" if fr else "AGREED SERVICES"
    services_box = (
        f'<div class="c-services-box"><div class="c-services-title">{svc_title}</div>'
        f'<div class="c-stags">{stags}</div></div>'
        if services
        else ""
    )
    desc_label = "D\u00e9tail des travaux\u202f:" if fr else "Works description:"
    desc_html = (
        f'<div class="highlight"><strong>{desc_label}</strong><br>'
        + _esc(c.description_travaux).replace("\n", "<br>")
        + "</div>"
        if c.description_travaux
        else ""
    )

    # ART OBJET
    _add(
        "OBJET DU CONTRAT" if fr else "SCOPE OF AGREEMENT",
        (
            f"""
        <p>Le pr\u00e9sent contrat a pour objet la r\u00e9alisation par <strong>CASA DI LUSSO SARL</strong>
        (ci-apr\u00e8s \u00ab\u202fLe Prestataire\u202f\u00bb) de travaux et prestations de type
        <strong>{type_label}</strong> dans le bien immobilier du Client.</p>
        <p><strong>Type de bien\u202f:</strong> {type_bien_lbl}{surface_str}</p>
        <p><strong>Adresse du chantier\u202f:</strong> {_esc(c.adresse_travaux) or
                                                        "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026"}</p>
        {services_box}
        {desc_html}
        <p>Tout travail ou prestation non mentionn\u00e9(e) express\u00e9ment au pr\u00e9sent article est
        <strong>formellement exclu(e)</strong> du pr\u00e9sent contrat et ne pourra \u00eatre r\u00e9clam\u00e9(e)
        sans nouvel accord contractuel \u00e9crit.</p>"""
            if fr
            else f"""
        <p>This contract covers the execution by <strong>CASA DI LUSSO SARL</strong>
        (hereinafter \u201cThe Service Provider\u201d) of works and services of type
        <strong>{type_label}</strong> at the Client\u2019s property.</p>
        <p><strong>Property type:</strong> {type_bien_lbl}{surface_str}</p>
        <p><strong>Site address:</strong> {_esc(c.adresse_travaux) or
                                           "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026"}</p>
        {services_box}
        {desc_html}
        <p>Any work or service not expressly mentioned in this article is
        <strong>excluded</strong> and may not be claimed
        without a new written agreement.</p>"""
        ),
    )

    # ART PLANNING (conditional)
    if c.date_debut or c.duree_estimee:
        d_str = _fmt_date(c.date_debut) if c.date_debut else ""
        dur = _esc(c.duree_estimee) if c.duree_estimee else ""
        cards = ""
        if d_str:
            lbl = "Date de d\u00e9but" if fr else "Start Date"
            cards += f'<div class="plan-card"><div class="plan-card-label">{lbl}</div><div class="plan-card-val">{d_str}</div></div>'
        if dur:
            lbl = "Dur\u00e9e estim\u00e9e" if fr else "Estimated Duration"
            cards += f'<div class="plan-card"><div class="plan-card-label">{lbl}</div><div class="plan-card-val">{dur}</div></div>'
        if d_str and dur:
            lbl = "Livraison pr\u00e9visionnelle" if fr else "Expected Delivery"
            val = "Selon planning" if fr else "As per schedule"
            cards += f'<div class="plan-card"><div class="plan-card-label">{lbl}</div><div class="plan-card-val">{val}</div></div>'
        _add(
            (
                "PLANNING &amp; D\u00c9LAIS D\u2019EX\u00c9CUTION"
                if fr
                else "SCHEDULE &amp; EXECUTION TIMELINE"
            ),
            (
                f"""
            <div class="plan-grid">{cards}</div>
            <p>Le planning communiqu\u00e9 est <strong>estimatif</strong> et non contractuellement opposable.
            Le Prestataire mettra tout en \u0153uvre pour respecter les d\u00e9lais convenus, sous r\u00e9serve de la
            bonne ex\u00e9cution des obligations du Client (paiements, validations, acc\u00e8s chantier).
            Tout retard imputable au Client entra\u00eene automatiquement un d\u00e9calage du planning sans
            possibilit\u00e9 d\u2019invoquer une quelconque p\u00e9nalit\u00e9 \u00e0 l\u2019encontre du Prestataire.</p>"""
                if fr
                else f"""
            <div class="plan-grid">{cards}</div>
            <p>The communicated schedule is <strong>indicative</strong> and not contractually binding.
            The Service Provider will make every effort to meet agreed timelines, subject to the Client’s timely
            fulfillment of obligations (payments, approvals, site access).
            Any delay attributable to the Client automatically pushes the schedule back with no right
            to invoke penalties against the Service Provider.</p>"""
            ),
        )

    # ART FORCE CONTRACTUELLE
    _add(
        "FORCE CONTRACTUELLE ET PREUVE" if fr else "CONTRACTUAL FORCE AND EVIDENCE",
        (
            """
        <p>Le pr\u00e9sent contrat, le devis sign\u00e9 par les deux parties, les plans et visuels approuv\u00e9s
        par \u00e9crit, ainsi que toutes les confirmations officielles \u00e9crites, constituent
        <strong>la base l\u00e9gale exclusive et exhaustive</strong> des engagements r\u00e9ciproques des parties.</p>
        <ul>
          <li>Tout \u00e9change oral, r\u00e9union informelle, discussion t\u00e9l\u00e9phonique ou message non valid\u00e9
          officiellement par voie \u00e9crite ou \u00e9lectronique <strong>n\u2019a aucune valeur contractuelle</strong>.</li>
          <li>Les messages WhatsApp, SMS, e-mails et tout document sign\u00e9 ou valid\u00e9 par le Client
          <strong>font foi</strong> et peuvent \u00eatre produits comme preuves en cas de litige.</li>
          <li>Toute modification au pr\u00e9sent contrat doit faire l\u2019objet d\u2019un
          <strong>avenant \u00e9crit sign\u00e9</strong> par les deux parties pour \u00eatre valide.</li>
        </ul>
        <div class="highlight">En cas de contradiction entre le pr\u00e9sent contrat et tout autre document,
        <strong>le pr\u00e9sent contrat prime</strong>, sauf avenant sign\u00e9 post\u00e9rieurement.</div>"""
            if fr
            else """
        <p>This contract, the quotation signed by both parties, written and approved plans,
        and all official written confirmations, constitutes
        <strong>the sole and exhaustive legal basis</strong> of the parties\u2019 mutual commitments.</p>
        <ul>
          <li>Any oral exchange, informal meeting, telephone discussion, or unvalidated message <strong>has no contractual value</strong>.</li>
          <li>WhatsApp messages, SMS, emails, and any document signed or validated by the Client
          <strong>shall serve as evidence</strong> and may be produced in any dispute.</li>
          <li>Any modification to this contract must be formalized by a
          <strong>written amendment signed</strong> by both parties.</li>
        </ul>
        <div class="highlight">In case of contradiction between this contract and any other document,
        <strong>this contract prevails</strong>, unless a later signed amendment exists.</div>"""
        ),
    )

    # ART OBLIGATIONS PRESTATAIRE
    resp_str = (
        f"<p><strong>{'Responsable de projet d\u00e9sign\u00e9\u202f:' if fr else 'Designated Project Manager:'}</strong> {_esc(c.responsable_projet)}</p>"
        if c.responsable_projet
        else ""
    )
    arch_str = (
        f"<p><strong>{'Architecte / Designer associ\u00e9\u202f:' if fr else 'Associated Architect / Designer:'}</strong> {_esc(c.architecte)}</p>"
        if c.architecte
        else ""
    )
    _add(
        "OBLIGATIONS DU PRESTATAIRE" if fr else "SERVICE PROVIDER OBLIGATIONS",
        (
            f"""
        <p>Le Prestataire s\u2019engage \u00e0\u202f:</p>
        <ul>
          <li>Ex\u00e9cuter les travaux conform\u00e9ment aux <strong>r\u00e8gles de l\u2019art</strong> et aux normes techniques marocaines en vigueur.</li>
          <li>Mettre \u00e0 disposition une <strong>\u00e9quipe qualifi\u00e9e et exp\u00e9riment\u00e9e</strong>, sous la supervision d\u2019un responsable de chantier d\u00e9sign\u00e9.</li>
          <li>Respecter les choix esth\u00e9tiques et techniques <strong>valid\u00e9s par \u00e9crit</strong> par le Client.</li>
          <li>Informer le Client de tout al\u00e9a ou difficult\u00e9 susceptible d\u2019affecter le planning ou le budget.</li>
          <li>Veiller au maintien d\u2019un chantier <strong>propre et s\u00e9curis\u00e9</strong> tout au long de l\u2019ex\u00e9cution.</li>
          <li>Assurer la coordination entre les diff\u00e9rents corps de m\u00e9tier intervenants.</li>
        </ul>
        {resp_str}{arch_str}
        <div class="highlight">Le Prestataire est tenu \u00e0 une <strong>obligation de moyen</strong> et non de
        r\u00e9sultat pour les travaux dont les mat\u00e9riaux, choix esth\u00e9tiques et contraintes sp\u00e9cifiques sont
        impos\u00e9s par le Client.</div>"""
            if fr
            else f"""
        <p>The Service Provider undertakes to:</p>
        <ul>
          <li>Execute works in compliance with <strong>professional standards</strong> and applicable Moroccan technical regulations.</li>
          <li>Provide a <strong>qualified and experienced team</strong>, under the supervision of a designated site manager.</li>
          <li>Respect aesthetic and technical choices <strong>validated in writing</strong> by the Client.</li>
          <li>Inform the Client of any hazard or difficulty likely to affect the schedule or budget.</li>
          <li>Maintain a <strong>clean and safe worksite</strong> throughout execution.</li>
          <li>Coordinate between the various trades involved.</li>
        </ul>
        {resp_str}{arch_str}
        <div class="highlight">The Service Provider is bound by a <strong>best-efforts obligation</strong>
        (not a results obligation) for works where materials, aesthetic choices, and specific constraints are
        imposed by the Client.</div>"""
        ),
    )

    # ART OBLIGATIONS CLIENT
    acces_extra = f" ({_esc(c.conditions_acces)})" if c.conditions_acces else ""
    _add(
        (
            "OBLIGATIONS RENFORC\u00c9ES DU CLIENT"
            if fr
            else "REINFORCED CLIENT OBLIGATIONS"
        ),
        (
            f"""
        <p>Le Client s\u2019engage contractuellement et irr\u00e9vocablement \u00e0\u202f:</p>
        <ul>
          <li><strong>Respecter</strong> l\u2019ensemble des membres de l\u2019\u00e9quipe du Prestataire et leurs d\u00e9cisions techniques professionnelles.</li>
          <li>Fournir toutes les <strong>validations \u00e9crites</strong> (plans, choix de mat\u00e9riaux, modifications) dans des d\u00e9lais raisonnables n\u2019exc\u00e9dant pas 72h, sauf accord contraire.</li>
          <li>R\u00e9gler les <strong>paiements aux dates convenues</strong> dans l\u2019\u00e9ch\u00e9ancier contractuel.</li>
          <li>N\u2019exercer aucune pression, menace, intimidation ni contrainte sur les \u00e9quipes, les sous-traitants ou les fournisseurs du Prestataire.</li>
          <li>Garantir un <strong>acc\u00e8s libre, s\u00e9curis\u00e9 et continu</strong> au chantier selon les conditions convenues.{acces_extra}</li>
          <li><strong>Assumer l\u2019enti\u00e8re responsabilit\u00e9</strong> de toutes les d\u00e9cisions esth\u00e9tiques et techniques qu\u2019il a valid\u00e9es par \u00e9crit.</li>
          <li>S\u2019abstenir de faire intervenir <strong>toute autre entreprise ou artisan</strong> sur le chantier sans accord pr\u00e9alable \u00e9crit du Prestataire.</li>
          <li>Assurer la pr\u00e9sence d\u2019un repr\u00e9sentant habilit\u00e9 \u00e0 <strong>prendre des d\u00e9cisions</strong> lors des r\u00e9unions de chantier planifi\u00e9es.</li>
        </ul>
        <div class="warning-box">\u26a0\ufe0f En cas de non-respect de l\u2019une de ces obligations, le Prestataire se r\u00e9serve le droit de
        <strong>suspendre imm\u00e9diatement les travaux</strong> sans pr\u00e9avis ni indemnit\u00e9, et de facturer les
        frais de red\u00e9marrage pr\u00e9vus au pr\u00e9sent contrat.</div>"""
            if fr
            else f"""
        <p>The Client contractually and irrevocably undertakes to:</p>
        <ul>
          <li><strong>Respect</strong> all members of the Service Provider\u2019s team and their professional technical decisions.</li>
          <li>Provide all <strong>written validations</strong> (plans, material choices, modifications) within reasonable timeframes not exceeding 72 hours, unless otherwise agreed.</li>
          <li>Make <strong>payments on the agreed dates</strong> in the contractual schedule.</li>
          <li>Not exert any pressure, threats, intimidation, or constraint on the teams, subcontractors, or suppliers.</li>
          <li>Guarantee <strong>free, secure, and continuous site access</strong> under the agreed conditions.{acces_extra}</li>
          <li>Take <strong>full responsibility</strong> for all aesthetic and technical decisions validated in writing.</li>
          <li>Refrain from having <strong>any other company or tradesperson</strong> on site without prior written consent from the Service Provider.</li>
          <li>Ensure the presence of an authorized representative empowered to make decisions at scheduled site meetings.</li>
        </ul>
        <div class="warning-box">\u26a0\ufe0f In case of non-compliance, the Service Provider reserves the right to <strong>immediately suspend works</strong> without notice or compensation, and to invoice the restart fees provided in this contract.</div>"""
        ),
    )

    # ART DÉLAIS ET ALÉAS
    _add(
        (
            "D\u00c9LAIS, RETARDS ET AL\u00c9AS"
            if fr
            else "TIMELINES, DELAYS AND CONTINGENCIES"
        ),
        (
            """
        <p>Le Prestataire ne saurait \u00eatre tenu responsable de tout retard r\u00e9sultant des causes ci-apr\u00e8s
        list\u00e9es, qui constituent autant de <strong>cas de suspension automatique</strong> du d\u00e9lai contractuel\u202f:</p>
        <ul>
          <li>Retard ou d\u00e9faut de paiement de la part du Client au-del\u00e0 du d\u00e9lai tol\u00e9r\u00e9\u202f;</li>
          <li>Retard du Client dans la validation des plans, choix de mat\u00e9riaux ou modifications\u202f;</li>
          <li>Changement de design ou de prestation d\u00e9cid\u00e9 apr\u00e8s validation initiale\u202f;</li>
          <li>Retard d\u2019importation, rupture de stock chez les fournisseurs ou d\u00e9lais douaniers\u202f;</li>
          <li>Cas de force majeure (pand\u00e9mie, catastrophe naturelle, conflit, d\u00e9cision administrative)\u202f;</li>
          <li>Probl\u00e8me structurel impr\u00e9vu d\u00e9couvert en cours de chantier\u202f;</li>
          <li>Intervention de tiers non mandat\u00e9s par le Prestataire\u202f;</li>
          <li>D\u00e9faut d\u2019acc\u00e8s au chantier.</li>
        </ul>
        <div class="highlight">Tout retard imputable au Client <strong>repousse automatiquement</strong> le planning
        d\u2019un nombre de jours \u00e9quivalent, sans possibilit\u00e9 pour le Client d\u2019invoquer une quelconque
        p\u00e9nalit\u00e9 \u00e0 l\u2019encontre du Prestataire.</div>"""
            if fr
            else """
        <p>The Service Provider cannot be held liable for any delay resulting from the following causes,
        which constitute automatic <strong>suspension of the contractual timeline</strong>:</p>
        <ul>
          <li>Late or missing payment from the Client beyond the tolerated delay;</li>
          <li>Client delay in validating plans, material choices, or modifications;</li>
          <li>Design or scope changes decided after initial validation;</li>
          <li>Import delays, supplier stock shortages, or customs issues;</li>
          <li>Force majeure (pandemic, natural disaster, conflict, administrative order);</li>
          <li>Unforeseen structural issues discovered during works;</li>
          <li>Unauthorized third-party interventions;</li>
          <li>Denied or blocked site access.</li>
        </ul>
        <div class="highlight">Any delay attributable to the Client <strong>automatically extends</strong> the timeline
        by the equivalent number of days, with no right for the Client to invoke penalties against the Service Provider.</div>"""
        ),
    )

    # ART MODIFICATIONS
    _add(
        (
            "MODIFICATIONS, AVENANTS ET TRAVAUX SUPPL\u00c9MENTAIRES"
            if fr
            else "MODIFICATIONS, AMENDMENTS AND ADDITIONAL WORKS"
        ),
        (
            """
        <p>Le p\u00e9rim\u00e8tre des travaux d\u00e9fini \u00e0 l\u2019Article\u00a01 est ferme et d\u00e9finitif \u00e0 compter de la date de
        signature. Toute modification ult\u00e9rieure est soumise aux r\u00e8gles suivantes\u202f:</p>
        <ol>
          <li>La demande de modification doit \u00eatre formul\u00e9e <strong>par \u00e9crit</strong> (email ou document sign\u00e9).</li>
          <li>Le Prestataire \u00e9tablira un <strong>devis compl\u00e9mentaire</strong> dans un d\u00e9lai raisonnable.</li>
          <li>La modification ne sera ex\u00e9cut\u00e9e qu\u2019apr\u00e8s <strong>signature du devis additionnel</strong> et versement de l\u2019acompte correspondant.</li>
          <li>Tout changement entra\u00eene une <strong>r\u00e9vision du planning</strong> \u00e0 la hausse ou \u00e0 la baisse selon la nature des travaux.</li>
          <li>Les <strong>moins-values</strong> (r\u00e9ductions de prestations) n\u2019ouvrent pas droit au remboursement des sommes d\u00e9j\u00e0 vers\u00e9es.</li>
        </ol>
        <div class="warning-box">\u26a0\ufe0f <strong>Aucune modification verbale</strong> ne sera prise en compte.
        Tout travail suppl\u00e9mentaire ex\u00e9cut\u00e9 sans avenant sign\u00e9 sera factur\u00e9 sur la base du tarif
        horaire en vigueur du Prestataire.</div>"""
            if fr
            else """
        <p>The works scope defined in Article 1 is firm and final from the signing date. Any subsequent modification is subject to the following rules:</p>
        <ol>
          <li>Any modification request must be made <strong>in writing</strong> (email or signed document).</li>
          <li>The Service Provider will issue a <strong>supplementary quotation</strong> within a reasonable timeframe.</li>
          <li>The modification will only be executed after <strong>signing the additional quotation</strong> and payment of the corresponding deposit.</li>
          <li>Any change entails a <strong>revision of the timeline</strong>, up or down, depending on the nature of works.</li>
          <li><strong>Reductions</strong> in scope do not entitle the Client to a refund of amounts already paid.</li>
        </ol>
        <div class="warning-box">\u26a0\ufe0f <strong>No verbal modification</strong> will be considered. Any additional work performed without a signed amendment will be invoiced at the Service Provider\u2019s current hourly rate.</div>"""
        ),
    )

    # ART CONDITIONS FINANCIÈRES
    montant_ht = float(c.montant_ht or 0)
    tva_pct = float(c.tva or 0)
    montant_tva = montant_ht * tva_pct / 100
    montant_ttc = montant_ht + montant_tva
    devise = c.devise or "MAD"
    mode_label = MODE_NAMES[lang].get(
        c.mode_paiement_texte or "virement", c.mode_paiement_texte or ""
    )
    tranches = c.tranches if isinstance(c.tranches, list) else []
    tot_pct = sum(float(t.get("pourcentage", 0)) for t in tranches)
    tva_note = (
        (" (non assujetti TVA)" if fr else " (VAT-exempt)")
        if tva_pct == 0
        else (
            f" \u2014 {'TVA' if fr else 'VAT'}\u00a0{int(tva_pct)}%\u202f: {_fmt_amt(montant_tva, devise)}"
            f" \u2014 <strong>{'TTC' if fr else 'Incl. tax'}\u202f: {_fmt_amt(montant_ttc, devise)}</strong>"
        )
    )
    tr_rows = ""
    for i, tr in enumerate(tranches):
        pct = float(tr.get("pourcentage", 0))
        amt = montant_ttc * pct / 100
        lbl = _esc(tr.get("label", f"Tranche {i + 1}"))
        row_cls = "even" if i % 2 == 1 else ""
        tr_rows += (
            f'<tr class="{row_cls}"><td>{i + 1}</td><td>{lbl}</td>'
            f'<td style="text-align:center">{int(pct)}%</td>'
            f'<td class="mono">{_fmt_amt(amt, devise)}</td></tr>'
        )
    rib_str = f" \u2014 {_esc(c.rib)}" if c.rib else ""
    delai_ret = c.delai_retard if c.delai_retard is not None else 5
    penalite_label = _format_penalite_retard(c, lang)
    frais_li = (
        (
            f"<li>Des <strong>frais de red\u00e9marrage</strong> d\u2019un montant de "
            f"<strong>{_fmt_amt(float(c.frais_redemarrage), devise)}</strong> seront factur\u00e9s "
            f"avant toute reprise des travaux\u202f;</li>"
            if fr
            else f"<li><strong>Restart fees</strong> of <strong>{_fmt_amt(float(c.frais_redemarrage), devise)}</strong> "
            f"will be invoiced before any resumption of works;</li>"
        )
        if c.frais_redemarrage
        else ""
    )
    ht_label = "Montant total HT\u202f:" if fr else "Total amount (excl. tax):"
    desc_th = "Description"
    amt_th = "Montant" if fr else "Amount"
    mode_lbl = "Mode de r\u00e8glement\u202f:" if fr else "Payment method:"
    _add(
        (
            "CONDITIONS FINANCI\u00c8RES ET IRR\u00c9VOCABILIT\u00c9 DES PAIEMENTS"
            if fr
            else "FINANCIAL CONDITIONS AND PAYMENT IRREVOCABILITY"
        ),
        (
            f"""
        <p><strong>{ht_label}</strong> {_fmt_amt(montant_ht, devise)}{tva_note}</p>
        <p>Les paiements sont \u00e9chelonn\u00e9s selon le tableau ci-apr\u00e8s. Chaque versement est une
        condition suspensive \u00e0 la poursuite des travaux\u202f:</p>
        <table class="pay-table">
          <thead><tr><th>#</th><th>{desc_th}</th><th>%</th><th>{amt_th}</th></tr></thead>
          <tbody>{tr_rows}</tbody>
          <tfoot><tr class="ptotal">
            <td colspan="2"><strong>TOTAL</strong></td>
            <td style="text-align:center"><strong>{int(tot_pct)}%</strong></td>
            <td class="mono"><strong>{_fmt_amt(montant_ttc, devise)}</strong></td>
          </tr></tfoot>
        </table>
        <p><strong>{mode_lbl}</strong> {mode_label}{rib_str}</p>
        <ul>
          <li>Tout acompte vers\u00e9 est <strong>d\u00e9finitivement acquis au Prestataire</strong> et non
          remboursable, sauf faute lourde d\u00fbment constat\u00e9e par d\u00e9cision judiciaire d\u00e9finitive.</li>
          <li>En cas de retard de paiement sup\u00e9rieur \u00e0 <strong>{delai_ret} jours</strong> calendaires\u202f:
            <ul>
              <li>Les travaux sont <strong>imm\u00e9diatement suspendus</strong> et les \u00e9quipes retir\u00e9es du chantier\u202f;</li>
              <li>Des <strong>p\u00e9nalit\u00e9s de retard</strong> de <strong>{penalite_label}</strong> de retard sont automatiquement applicables sur les sommes dues\u202f;</li>
              {frais_li}
              <li>Le planning est automatiquement r\u00e9vis\u00e9 sans droit \u00e0 indemnit\u00e9 pour le Client.</li>
            </ul>
          </li>
        </ul>"""
            if fr
            else f"""
        <p><strong>{ht_label}</strong> {_fmt_amt(montant_ht, devise)}{tva_note}</p>
        <p>Payments are scheduled as follows. Each payment is a condition for the continuation of works:</p>
        <table class="pay-table">
          <thead><tr><th>#</th><th>{desc_th}</th><th>%</th><th>{amt_th}</th></tr></thead>
          <tbody>{tr_rows}</tbody>
          <tfoot><tr class="ptotal">
            <td colspan="2"><strong>TOTAL</strong></td>
            <td style="text-align:center"><strong>{int(tot_pct)}%</strong></td>
            <td class="mono"><strong>{_fmt_amt(montant_ttc, devise)}</strong></td>
          </tr></tfoot>
        </table>
        <p><strong>{mode_lbl}</strong> {mode_label}{rib_str}</p>
        <ul>
          <li>Any deposit paid is <strong>definitively retained by the Service Provider</strong> and non-refundable, except in case of serious fault established by final court decision.</li>
          <li>In case of payment delay exceeding <strong>{delai_ret} calendar days</strong>:
            <ul>
              <li>Works are <strong>immediately suspended</strong> and teams removed from site;</li>
              <li><strong>Late payment penalties</strong> of <strong>{penalite_label}</strong> automatically apply on overdue amounts;</li>
              {frais_li}
              <li>The schedule is automatically revised with no right to compensation for the Client.</li>
            </ul>
          </li>
        </ul>"""
        ),
    )

    # ART LIMITATION RESPONSABILITÉ
    _add(
        "LIMITATION DE RESPONSABILIT\u00c9" if fr else "LIMITATION OF LIABILITY",
        (
            f"""
        <p>La responsabilit\u00e9 du Prestataire est express\u00e9ment <strong>limit\u00e9e et exclusivement
        engag\u00e9e</strong> pour les travaux qu\u2019il a lui-m\u00eame r\u00e9alis\u00e9s. Le Prestataire est formellement
        <strong>d\u00e9gag\u00e9 de toute responsabilit\u00e9</strong> pour\u202f:</p>
        <ul>
          <li>Les <strong>d\u00e9fauts structurels</strong> pr\u00e9existants ou d\u00e9couverts en cours de chantier\u202f;</li>
          <li>Les <strong>infiltrations</strong> et probl\u00e8mes provenant d\u2019\u00e9l\u00e9ments ext\u00e9rieurs au p\u00e9rim\u00e8tre du contrat\u202f;</li>
          <li>Les <strong>mat\u00e9riaux, produits ou \u00e9quipements</strong> fournis par le Client ou impos\u00e9s par lui\u202f;</li>
          <li>Les travaux r\u00e9alis\u00e9s par <strong>d\u2019autres entreprises ou artisans</strong> intervenant sur le chantier\u202f;</li>
          <li>Les d\u00e9g\u00e2ts r\u00e9sultant d\u2019un <strong>usage non conforme</strong>, de modifications, ou d\u2019un d\u00e9faut d\u2019entretien apr\u00e8s livraison\u202f;</li>
          <li>Les cons\u00e9quences des <strong>d\u00e9cisions esth\u00e9tiques ou techniques</strong> valid\u00e9es par le Client.</li>
        </ul>
        <div class="warning-box">La responsabilit\u00e9 totale du Prestataire, toutes causes confondues,
        est <strong>strictement plafonn\u00e9e au montant total TTC effectivement encaiss\u00e9</strong>
        dans le cadre du pr\u00e9sent contrat.</div>"""
            if fr
            else f"""
        <p>The Service Provider\u2019s liability is expressly <strong>limited and exclusively engaged</strong>
        for works it has itself carried out. The Service Provider is formally
        <strong>released from all liability</strong> for:</p>
        <ul>
          <li>Pre-existing or in-progress <strong>structural defects</strong>;</li>
          <li><strong>Infiltrations</strong> and issues from elements outside the contract scope;</li>
          <li><strong>Materials, products, or equipment</strong> supplied or imposed by the Client;</li>
          <li>Works carried out by <strong>other companies or tradespeople</strong> on site;</li>
          <li>Damage resulting from <strong>improper use</strong>, modifications, or lack of maintenance after delivery;</li>
          <li>Consequences of <strong>aesthetic or technical decisions</strong> validated by the Client.</li>
        </ul>
        <div class="warning-box">The Service Provider\u2019s total liability, for all causes, is
        <strong>strictly capped at the total amount actually received</strong> under this contract.</div>"""
        ),
    )

    # ART RÉCEPTION
    delai_res = c.delai_reserves if c.delai_reserves is not None else 7
    _add(
        (
            "R\u00c9CEPTION ET LIVRAISON DES TRAVAUX"
            if fr
            else "ACCEPTANCE AND DELIVERY OF WORKS"
        ),
        (
            f"""
        <p><strong>R\u00e9ception provisoire\u202f:</strong> Elle est effectu\u00e9e en pr\u00e9sence physique et obligatoire
        du Client (ou de son repr\u00e9sentant mandat\u00e9 par \u00e9crit). Un
        <strong>proc\u00e8s-verbal de r\u00e9ception</strong> sera \u00e9tabli et sign\u00e9 par les deux parties.</p>
        <p>Toute <strong>r\u00e9serve</strong> (malfa\u00e7on, non-conformit\u00e9) doit \u00eatre formul\u00e9e de mani\u00e8re pr\u00e9cise
        et par \u00e9crit dans un d\u00e9lai de <strong>{delai_res} jours ouvr\u00e9s</strong> suivant la r\u00e9ception
        provisoire.</p>
        <ul>
          <li>Les r\u00e9serves mentionn\u00e9es feront l\u2019objet d\u2019une <strong>reprise contradictoire</strong> dans un d\u00e9lai raisonnable.</li>
          <li>Pass\u00e9 le d\u00e9lai de {delai_res} jours sans r\u00e9serve \u00e9crite, les travaux sont r\u00e9put\u00e9s <strong>r\u00e9ceptionn\u00e9s d\u00e9finitivement et sans r\u00e9serve</strong>.</li>
          <li>La r\u00e9ception vaut <strong>point de d\u00e9part</strong> du d\u00e9lai de garantie.</li>
        </ul>
        <div class="highlight">L\u2019absence du Client \u00e0 la r\u00e9ception, sans d\u00e9l\u00e9gation \u00e9crite pr\u00e9alable,
        vaut <strong>acceptation tacite</strong> des travaux sans r\u00e9serve.</div>"""
            if fr
            else f"""
        <p><strong>Provisional acceptance:</strong> Carried out with the Client (or their duly mandated representative) present. A <strong>formal acceptance report</strong> will be drafted and signed by both parties.</p>
        <p>Any <strong>reservations</strong> (defects, non-conformity) must be precisely stated in writing within <strong>{delai_res} working days</strong> of provisional acceptance.</p>
        <ul>
          <li>Stated reservations will be subject to a <strong>jointly supervised correction</strong> within a reasonable timeframe.</li>
          <li>After {delai_res} days with no written reservation, works are deemed <strong>definitively accepted without reservation</strong>.</li>
          <li>Acceptance marks the <strong>start date</strong> of the warranty period.</li>
        </ul>
        <div class="highlight">The Client\u2019s absence at acceptance, without prior written delegation, constitutes <strong>tacit acceptance</strong> without reservation.</div>"""
        ),
    )

    # ART GARANTIE
    lang_key = "fr" if fr else "en"
    garantie = (
        GARANTIE_LABELS.get(lang_key, {}).get(c.garantie, _esc(c.garantie))
        if c.garantie
        else ("1 an" if fr else "1 year")
    )
    _add(
        "GARANTIE ET APR\u00c8S-LIVRAISON" if fr else "WARRANTY AND POST-DELIVERY",
        (
            f"""
        <p>Le Prestataire accorde une <strong>garantie contractuelle de {garantie}</strong> sur les
        travaux r\u00e9alis\u00e9s dans le cadre du pr\u00e9sent contrat, \u00e0 compter de la date de r\u00e9ception
        d\u00e9finitive.</p>
        <p>Cette garantie couvre les <strong>d\u00e9fauts d\u2019ex\u00e9cution</strong> directement imputables aux
        travaux du Prestataire, \u00e0 l\u2019exclusion de\u202f:</p>
        <ul>
          <li>L\u2019usure normale li\u00e9e \u00e0 l\u2019utilisation\u202f;</li>
          <li>Les d\u00e9gradations caus\u00e9es par le Client, ses locataires ou des tiers\u202f;</li>
          <li>Les interventions de tiers sur les travaux garantis\u202f;</li>
          <li>Un d\u00e9faut d\u2019entretien ou une utilisation non conforme \u00e0 la destination des travaux\u202f;</li>
          <li>Les probl\u00e8mes structurels non li\u00e9s aux travaux r\u00e9alis\u00e9s.</li>
        </ul>
        <p>La mise en jeu de la garantie requiert une <strong>notification \u00e9crite</strong> d\u00e9taill\u00e9e
        adress\u00e9e au Prestataire avec photos \u00e0 l\u2019appui.</p>"""
            if fr
            else f"""
        <p>The Service Provider grants a <strong>contractual warranty of {garantie}</strong> on works performed under this contract, from the definitive acceptance date.</p>
        <p>This warranty covers <strong>execution defects</strong> directly attributable to the Service Provider's works, excluding:</p>
        <ul>
          <li>Normal wear from use;</li>
          <li>Damage caused by the Client, tenants or third parties;</li>
          <li>Third-party interventions on warranted works;</li>
          <li>Lack of maintenance or improper use;</li>
          <li>Structural issues unrelated to the works performed.</li>
        </ul>
        <p>Invoking the warranty requires a <strong>detailed written notification</strong> sent to the Service Provider with supporting photos.</p>"""
        ),
    )

    if "c-comportement" in clauses:
        _add(
            (
                "CLAUSE DE COMPORTEMENT ET PROTECTION DES \u00c9QUIPES"
                if fr
                else "CONDUCT AND TEAM PROTECTION CLAUSE"
            ),
            (
                """
            <p>Le Client s\u2019engage formellement \u00e0 maintenir des relations <strong>respectueuses et
            professionnelles</strong> avec l\u2019ensemble du personnel, des sous-traitants et des
            fournisseurs du Prestataire.</p>
            <p>Constituent des motifs de <strong>r\u00e9siliation imm\u00e9diate</strong> et sans indemnit\u00e9
            pour le Prestataire\u202f:</p>
            <ul>
              <li>Tout comportement abusif, humiliant, discriminatoire ou mena\u00e7ant envers les \u00e9quipes\u202f;</li>
              <li>Toute pression ou intimidation visant \u00e0 obtenir des prestations non contractuelles\u202f;</li>
              <li>Toute ing\u00e9rence non autoris\u00e9e dans les d\u00e9cisions techniques du Prestataire\u202f;</li>
              <li>Tout d\u00e9nigrement public du Prestataire ou de ses \u00e9quipes.</li>
            </ul>
            <div class="warning-box">En cas de r\u00e9siliation pour comportement abusif,
            <strong>toutes les sommes d\u00e9j\u00e0 vers\u00e9es restent d\u00e9finitivement acquises</strong>
            au Prestataire, et les travaux en cours seront factur\u00e9s au prorata.</div>"""
                if fr
                else """
            <p>The Client formally undertakes to maintain <strong>respectful and professional</strong> relations with all staff, subcontractors and suppliers of the Service Provider.</p>
            <p>The following constitute grounds for <strong>immediate termination</strong> without compensation for the Service Provider:</p>
            <ul>
              <li>Any abusive, humiliating, discriminatory, or threatening behavior toward teams;</li>
              <li>Any pressure or intimidation to obtain non-contractual services;</li>
              <li>Any unauthorized interference in the Service Provider's technical decisions;</li>
              <li>Any public disparagement of the Service Provider or its teams.</li>
            </ul>
            <div class="warning-box">In case of termination for abusive behavior, <strong>all amounts already paid remain definitively retained</strong> by the Service Provider, and works in progress will be invoiced pro-rata.</div>"""
            ),
        )

    if "c-prop-intel" in clauses:
        _add(
            "PROPRI\u00c9T\u00c9 INTELLECTUELLE" if fr else "INTELLECTUAL PROPERTY",
            (
                """
            <p>L\u2019ensemble des cr\u00e9ations r\u00e9alis\u00e9es dans le cadre du pr\u00e9sent contrat \u2014 incluant sans
            limitation les <strong>plans, dessins, moodboards, visuels, concepts d\u2019am\u00e9nagement,
            id\u00e9es cr\u00e9atives, prototypes et \u00e9tudes</strong> \u2014 demeurent la
            <strong>propri\u00e9t\u00e9 intellectuelle exclusive et inali\u00e9nable</strong> de CASA DI LUSSO SARL.</p>
            <p>Le Client b\u00e9n\u00e9ficie d\u2019une <strong>licence d\u2019utilisation personnelle</strong> pour le bien
            objet du contrat uniquement. Il lui est formellement interdit de\u202f:</p>
            <ul>
              <li>Reproduire, adapter ou diffuser ces cr\u00e9ations \u00e0 des fins commerciales ou publicitaires\u202f;</li>
              <li>Transmettre ou c\u00e9der ces documents \u00e0 des tiers\u202f;</li>
              <li>Utiliser ces cr\u00e9ations pour un bien immobilier diff\u00e9rent de celui vis\u00e9 au contrat\u202f;</li>
              <li>D\u00e9poser ces cr\u00e9ations \u00e0 titre de marque, brevet ou dessin industriel.</li>
            </ul>
            <p>Toute violation est susceptible d\u2019engager la <strong>responsabilit\u00e9 civile et p\u00e9nale</strong>
            du Client au titre du droit marocain de la propri\u00e9t\u00e9 intellectuelle.</p>"""
                if fr
                else """
            <p>All creations produced under this contract \u2014 including without limitation <strong>plans, drawings, moodboards, visuals, layout concepts, creative ideas, prototypes and studies</strong> \u2014 remain the <strong>exclusive and inalienable intellectual property</strong> of CASA DI LUSSO SARL.</p>
            <p>The Client is granted a <strong>personal use license</strong> for the property subject to this contract only. The Client is strictly prohibited from:</p>
            <ul>
              <li>Reproducing, adapting, or distributing these creations for commercial or advertising purposes;</li>
              <li>Transferring or assigning these documents to third parties;</li>
              <li>Using these creations for a property other than that specified in the contract;</li>
              <li>Registering these creations as a trademark, patent, or industrial design.</li>
            </ul>
            <p>Any violation may engage the Client’s <strong>civil and criminal liability</strong> under Moroccan intellectual property law.</p>"""
            ),
        )

    if "c-image" in clauses:
        _add(
            (
                "DROIT \u00c0 L\u2019IMAGE ET COMMUNICATION"
                if fr
                else "IMAGE RIGHTS AND COMMUNICATION"
            ),
            (
                """
            <p>Sauf refus <strong>expr\u00e8s et \u00e9crit</strong> notifi\u00e9 dans les 8 jours suivant la signature du
            pr\u00e9sent contrat, le Client autorise CASA DI LUSSO \u00e0\u202f:</p>
            <ul>
              <li>Photographier et filmer le chantier et le projet finalis\u00e9\u202f;</li>
              <li>Publier ces visuels sur son <strong>site internet, r\u00e9seaux sociaux, portfolio</strong>
              et supports de communication\u202f;</li>
              <li>Citer le projet \u00e0 titre de r\u00e9f\u00e9rence commerciale.</li>
            </ul>
            <p>Cette autorisation est conc\u00e9d\u00e9e \u00e0 titre <strong>gratuit, non exclusif et pour une dur\u00e9e
            illimit\u00e9e</strong>. Le Prestataire s\u2019engage \u00e0 ne jamais mentionner les informations personnelles
            du Client sans accord expr\u00e8s.</p>"""
                if fr
                else """
            <p>Unless <strong>express written objection</strong> is notified within 8 days of signing, the Client authorizes CASA DI LUSSO to:</p>
            <ul>
              <li>Photograph and film the worksite and completed project;</li>
              <li>Publish these visuals on its <strong>website, social media, portfolio</strong> and marketing materials;</li>
              <li>Reference the project as a commercial reference.</li>
            </ul>
            <p>This authorization is granted <strong>free of charge, non-exclusively and for an unlimited duration</strong>. The Service Provider undertakes never to mention the Client\u2019s personal information without express consent.</p>"""
            ),
        )

    if "c-confidential" in clauses:
        _add(
            "CONFIDENTIALIT\u00c9" if fr else "CONFIDENTIALITY",
            (
                """
            <p>Les deux parties s\u2019engagent mutuellement \u00e0 traiter comme <strong>strictement
            confidentielles</strong> toutes les informations \u00e9chang\u00e9es dans le cadre du pr\u00e9sent
            contrat, incluant notamment\u202f:</p>
            <ul>
              <li>Les montants financiers et conditions tarifaires\u202f;</li>
              <li>Les plans, documents techniques et sp\u00e9cifications du projet\u202f;</li>
              <li>Toute information relative aux m\u00e9thodes de travail du Prestataire.</li>
            </ul>
            <p>Cette obligation de confidentialit\u00e9 survit \u00e0 la <strong>r\u00e9siliation ou fin du
            contrat</strong> pour une dur\u00e9e de <strong>5 ans</strong>.</p>"""
                if fr
                else """
            <p>Both parties mutually undertake to treat as <strong>strictly confidential</strong> all information exchanged under this contract, including:</p>
            <ul>
              <li>Financial amounts and pricing conditions;</li>
              <li>Plans, technical documents and project specifications;</li>
              <li>Any information relating to the Service Provider\u2019s working methods.</li>
            </ul>
            <p>This confidentiality obligation survives <strong>termination or expiry</strong> of the contract for a period of <strong>5 years</strong>.</p>"""
            ),
        )

    if "c-sous-traiter" in clauses:
        _add(
            "DROIT DE SOUS-TRAITANCE" if fr else "SUBCONTRACTING RIGHTS",
            (
                """
            <p>Le Prestataire se r\u00e9serve le droit de <strong>recourir \u00e0 des sous-traitants</strong>
            qualifi\u00e9s pour l\u2019ex\u00e9cution de tout ou partie des travaux pr\u00e9vus au pr\u00e9sent contrat,
            notamment pour les corps de m\u00e9tier sp\u00e9cialis\u00e9s.</p>
            <p>Le Prestataire demeure <strong>seul responsable</strong> vis-\u00e0-vis du Client de la bonne
            ex\u00e9cution des travaux sous-trait\u00e9s. Le Client renonce express\u00e9ment \u00e0 invoquer la
            sous-traitance comme motif de contestation, d\u00e8s lors que les travaux sont conformes au
            pr\u00e9sent contrat.</p>"""
                if fr
                else """
            <p>The Service Provider reserves the right to <strong>engage qualified subcontractors</strong> for the execution of all or part of the works under this contract, particularly for specialized trades.</p>
            <p>The Service Provider remains <strong>solely responsible</strong> to the Client for the proper execution of subcontracted works. The Client expressly waives the right to invoke subcontracting as grounds for dispute, provided the works conform to this contract.</p>"""
            ),
        )

    if "c-materiau-prix" in clauses:
        _add(
            (
                "CLAUSE DE R\u00c9VISION DES PRIX MAT\u00c9RIAUX"
                if fr
                else "MATERIAL PRICE REVISION CLAUSE"
            ),
            (
                """
            <p>Dans l\u2019hypoth\u00e8se d\u2019une <strong>hausse des prix des mat\u00e9riaux sup\u00e9rieure \u00e0 10%</strong>
            par rapport aux prix de r\u00e9f\u00e9rence au jour de la signature, imputable \u00e0 des causes
            ext\u00e9rieures (inflation, rupture d\u2019approvisionnement, d\u00e9cision gouvernementale), le Prestataire se r\u00e9serve le droit de\u202f:</p>
            <ul>
              <li>Notifier le Client par \u00e9crit des nouvelles conditions tarifaires\u202f;</li>
              <li>Ajuster le montant du contrat \u00e0 hauteur de la hausse constat\u00e9e, apr\u00e8s accord \u00e9crit du Client.</li>
            </ul>
            <p>En cas de d\u00e9saccord, les parties s\u2019engagent \u00e0 <strong>n\u00e9gocier de bonne foi</strong>
            une solution dans un d\u00e9lai de 15 jours.</p>"""
                if fr
                else """
            <p>In the event of a <strong>material price increase exceeding 10%</strong> versus reference prices at signing, due to external causes (inflation, supply shortage, government decision), the Service Provider reserves the right to:</p>
            <ul>
              <li>Notify the Client in writing of the new pricing conditions;</li>
              <li>Adjust the contract amount proportionally to the increase, subject to the Client\u2019s written agreement.</li>
            </ul>
            <p>In case of disagreement, parties undertake to <strong>negotiate in good faith</strong> within 15 days.</p>"""
            ),
        )

    if "c-force-maj" in clauses:
        _add(
            "FORCE MAJEURE" if fr else "FORCE MAJEURE",
            (
                """
            <p>Aucune partie ne pourra \u00eatre tenue responsable de l\u2019inex\u00e9cution de ses obligations
            lorsque celle-ci r\u00e9sulte d\u2019un <strong>cas de force majeure</strong>, c\u2019est-\u00e0-dire d\u2019un
            \u00e9v\u00e9nement impr\u00e9visible, irr\u00e9sistible et ext\u00e9rieur aux parties, incluant notamment\u202f:</p>
            <ul>
              <li>Catastrophes naturelles, \u00e9pid\u00e9mies, pand\u00e9mies\u202f;</li>
              <li>Conflits arm\u00e9s, \u00e9meutes, actes terroristes\u202f;</li>
              <li>D\u00e9cisions gouvernementales ou administratives\u202f;</li>
              <li>Gr\u00e8ves g\u00e9n\u00e9rales affectant les secteurs d\u2019approvisionnement.</li>
            </ul>
            <p>La partie invoquant la force majeure doit en notifier l\u2019autre par
            <strong>\u00e9crit dans les 48 heures</strong>. Si la force majeure dure plus de
            <strong>60 jours cons\u00e9cutifs</strong>, chacune des parties pourra r\u00e9silier le contrat sans
            indemnit\u00e9, sous r\u00e9serve de r\u00e8glement des prestations d\u00e9j\u00e0 effectu\u00e9es.</p>"""
                if fr
                else """
            <p>Neither party shall be held liable for non-performance of obligations resulting from a <strong>force majeure event</strong>, being an unforeseeable, irresistible event beyond the parties\u2019 control, including without limitation:</p>
            <ul>
              <li>Natural disasters, epidemics, pandemics;</li>
              <li>Armed conflicts, riots, terrorist acts;</li>
              <li>Government or administrative orders;</li>
              <li>General strikes affecting supply chains.</li>
            </ul>
            <p>The invoking party must notify the other <strong>in writing within 48 hours</strong>. If force majeure lasts more than <strong>60 consecutive days</strong>, either party may terminate without compensation, subject to payment for works already performed.</p>"""
            ),
        )

    if "c-abandon-chant" in clauses:
        _add(
            "ABANDON DE CHANTIER PAR LE CLIENT" if fr else "CLIENT SITE ABANDONMENT",
            (
                """
            <p>Est consid\u00e9r\u00e9 comme <strong>abandon de chantier</strong> le fait pour le Client de
            refuser ou d\u2019emp\u00eacher l\u2019acc\u00e8s au chantier pendant plus de <strong>15 jours
            cons\u00e9cutifs</strong> sans justification valable et accept\u00e9e par le Prestataire.</p>
            <p>En cas d\u2019abandon de chantier, le Prestataire est en droit de\u202f:</p>
            <ul>
              <li>Facturer l\u2019int\u00e9gralit\u00e9 des travaux r\u00e9alis\u00e9s et mat\u00e9riaux command\u00e9s\u202f;</li>
              <li>Retenir d\u00e9finitivement l\u2019ensemble des sommes d\u00e9j\u00e0 vers\u00e9es\u202f;</li>
              <li>R\u00e9cup\u00e9rer tout mat\u00e9riel et outil lui appartenant\u202f;</li>
              <li>Facturer des <strong>indemnit\u00e9s d\u2019immobilisation</strong> pour les \u00e9quipes mobilis\u00e9es.</li>
            </ul>"""
                if fr
                else """
            <p><strong>Site abandonment</strong> occurs when the Client refuses or prevents site access for more than <strong>15 consecutive days</strong> without valid justification accepted by the Service Provider.</p>
            <p>In case of site abandonment, the Service Provider is entitled to:</p>
            <ul>
              <li>Invoice all completed works and ordered materials;</li>
              <li>Definitively retain all amounts already paid;</li>
              <li>Recover all equipment and tools belonging to it;</li>
              <li>Invoice <strong>immobilization indemnities</strong> for mobilized teams.</li>
            </ul>"""
            ),
        )

    if "c-non-debauch" in clauses:
        _add(
            (
                "CLAUSE DE NON-D\u00c9BAUCHAGE DU PERSONNEL"
                if fr
                else "NON-POACHING OF STAFF CLAUSE"
            ),
            (
                """
            <p>Le Client s\u2019engage, pendant la dur\u00e9e du pr\u00e9sent contrat et pendant une p\u00e9riode de
            <strong>24 mois</strong> suivant son terme ou sa r\u00e9siliation, \u00e0 ne pas directement ou
            indirectement\u202f:</p>
            <ul>
              <li>Recruter, solliciter ou engager tout membre du personnel ou sous-traitant du Prestataire\u202f;</li>
              <li>Inciter tout membre du personnel \u00e0 quitter le Prestataire.</li>
            </ul>
            <p>En cas de violation, le Client s\u2019engage \u00e0 verser au Prestataire une
            <strong>indemnit\u00e9 forfaitaire</strong> \u00e9quivalente \u00e0 <strong>12 mois de salaire brut</strong>
            de la personne concern\u00e9e.</p>"""
                if fr
                else """
            <p>The Client undertakes, for the duration of this contract and for a period of <strong>24 months</strong> following its end or termination, not to directly or indirectly:</p>
            <ul>
              <li>Recruit, solicit, or hire any member of the Service Provider\u2019s staff or subcontractors;</li>
              <li>Encourage any staff member to leave the Service Provider.</li>
            </ul>
            <p>In case of violation, the Client agrees to pay the Service Provider a <strong>lump-sum indemnity</strong> equivalent to <strong>12 months\u2019 gross salary</strong> of the person concerned.</p>"""
            ),
        )

    # ART RÉSILIATION
    _resil_n = _n[0] + 1  # predict the article number before _add increments
    _add(
        "R\u00c9SILIATION DU CONTRAT" if fr else "CONTRACT TERMINATION",
        (
            f"""
        <div class="sub-title">{_resil_n}.1 \u2013 R\u00e9siliation \u00e0 l\u2019initiative du Client</div>
        <p>Le Client peut mettre fin au pr\u00e9sent contrat par <strong>lettre recommand\u00e9e avec accus\u00e9 de
        r\u00e9ception</strong>. En pareil cas, le Client s\u2019engage \u00e0 r\u00e9gler\u202f:</p>
        <ul>
          <li>La totalit\u00e9 des travaux r\u00e9alis\u00e9s \u00e0 la date de r\u00e9siliation, au prorata\u202f;</li>
          <li>Le co\u00fbt de l\u2019ensemble des mat\u00e9riaux command\u00e9s, livr\u00e9s ou en cours de commande\u202f;</li>
          <li>Les frais de d\u00e9mobilisation des \u00e9quipes\u202f;</li>
          <li>Une <strong>indemnit\u00e9 de r\u00e9siliation</strong> de 15% du montant restant d\u00fb.</li>
        </ul>
        <p>L\u2019acompte initial vers\u00e9 \u00e0 l\u2019ouverture du chantier reste
        <strong>d\u00e9finitivement et irr\u00e9vocablement acquis</strong> au Prestataire.</p>
        <div class="sub-title">{_resil_n}.2 \u2013 R\u00e9siliation \u00e0 l\u2019initiative du Prestataire</div>
        <p>Le Prestataire peut r\u00e9silier le pr\u00e9sent contrat sans indemnit\u00e9 en cas de\u202f:</p>
        <ul>
          <li>Non-paiement d\u2019une ou plusieurs tranches au-del\u00e0 du d\u00e9lai tol\u00e9r\u00e9\u202f;</li>
          <li>Comportement abusif, mena\u00e7ant ou irrespectueux envers les \u00e9quipes\u202f;</li>
          <li>Blocage r\u00e9p\u00e9t\u00e9 et injustifi\u00e9 du chantier\u202f;</li>
          <li>Refus r\u00e9p\u00e9t\u00e9 de fournir les validations n\u00e9cessaires \u00e0 l\u2019avancement des travaux\u202f;</li>
          <li>Insolvabilit\u00e9 ou redressement judiciaire du Client.</li>
        </ul>"""
            if fr
            else f"""
        <div class="sub-title">{_resil_n}.1 \u2013 Termination by the Client</div>
        <p>The Client may terminate this contract by <strong>registered mail with acknowledgment of receipt</strong>. In such case, the Client undertakes to pay:</p>
        <ul>
          <li>All works completed at the termination date, on a pro-rata basis;</li>
          <li>The cost of all materials ordered, delivered, or on order;</li>
          <li>Team demobilization costs;</li>
          <li>A <strong>termination indemnity</strong> of 15% of the remaining amount due.</li>
        </ul>
        <p>The initial deposit paid at project start is <strong>definitively and irrevocably retained</strong> by the Service Provider.</p>
        <div class="sub-title">{_resil_n}.2 \u2013 Termination by the Service Provider</div>
        <p>The Service Provider may terminate without compensation in case of:</p>
        <ul>
          <li>Non-payment of one or more installments beyond the tolerated delay;</li>
          <li>Abusive, threatening, or disrespectful behavior toward teams;</li>
          <li>Repeated and unjustified site blockage;</li>
          <li>Repeated refusal to provide validations needed for works to progress;</li>
          <li>Client insolvency or receivership.</li>
        </ul>"""
        ),
    )

    # ART MÉDIATION (conditional)
    if "c-anti-litige" in clauses:
        tribunal = _esc(c.tribunal) if c.tribunal else "Tanger"
        _add(
            (
                "M\u00c9DIATION OBLIGATOIRE ET R\u00c8GLEMENT DES LITIGES"
                if fr
                else "MANDATORY MEDIATION AND DISPUTE RESOLUTION"
            ),
            (
                f"""
            <p>Avant tout recours judiciaire, les parties s\u2019engagent express\u00e9ment \u00e0 rechercher une
            <strong>solution amiable</strong> selon la proc\u00e9dure suivante\u202f:</p>
            <ol>
              <li>La partie plaignante adresse une <strong>mise en demeure \u00e9crite</strong> \u00e0 l\u2019autre partie par lettre recommand\u00e9e\u202f;</li>
              <li>L\u2019autre partie dispose de <strong>15 jours ouvr\u00e9s</strong> pour y r\u00e9pondre et proposer une solution\u202f;</li>
              <li>En l\u2019absence d\u2019accord dans un d\u00e9lai de <strong>30 jours</strong> suivant la mise en demeure, les parties peuvent saisir un m\u00e9diateur agr\u00e9\u00e9 d\u2019un commun accord\u202f;</li>
              <li>\u00c0 d\u00e9faut de m\u00e9diation aboutie, les parties pourront saisir les juridictions comp\u00e9tentes.</li>
            </ol>
            <p>Les parties conviennent d\u2019attribuer <strong>comp\u00e9tence exclusive</strong> aux juridictions
            commerciales du <strong>Tribunal de {tribunal}</strong> pour conna\u00eetre de tout litige relatif
            au pr\u00e9sent contrat.</p>
            <p>Le pr\u00e9sent contrat est r\u00e9gi et interpr\u00e9t\u00e9 conform\u00e9ment au <strong>droit marocain</strong>,
            notamment le Dahir des obligations et contrats (DOC).</p>"""
                if fr
                else f"""
            <p>Before any legal action, parties expressly undertake to seek an <strong>amicable solution</strong> through the following procedure:</p>
            <ol>
              <li>The complaining party sends a <strong>formal written notice</strong> to the other party by registered mail;</li>
              <li>The other party has <strong>15 working days</strong> to respond and propose a solution;</li>
              <li>Failing agreement within <strong>30 days</strong> of the formal notice, parties may jointly appoint an accredited mediator;</li>
              <li>Failing successful mediation, parties may refer to the competent courts.</li>
            </ol>
            <p>The parties agree to grant <strong>exclusive jurisdiction</strong> to the commercial courts of the <strong>Court of {tribunal}</strong> for any dispute arising from this contract.</p>
            <p>This contract is governed and interpreted in accordance with <strong>Moroccan law</strong>, in particular the Dahir of Obligations and Contracts (DOC).</p>"""
            ),
        )

    # ART LOI APPLICABLE
    excl_extra = (
        '<div class="art-divider"></div><p><strong>'
        + (
            "Exclusions contractuelles express\u00e9ment convenues\u202f:"
            if fr
            else "Expressly agreed exclusions:"
        )
        + "</strong><br>"
        + _esc(c.exclusions).replace("\n", "<br>")
        + "</p>"
        if c.exclusions
        else ""
    )
    spec_extra = (
        '<div class="art-divider"></div><p><strong>'
        + (
            "Clauses sp\u00e9cifiques additionnelles\u202f:"
            if fr
            else "Additional specific clauses:"
        )
        + "</strong><br>"
        + _esc(c.clause_spec).replace("\n", "<br>")
        + "</p>"
        if c.clause_spec
        else ""
    )
    annex_extra = (
        '<div class="highlight"><strong>'
        + (
            "Annexes jointes au pr\u00e9sent contrat\u202f:"
            if fr
            else "Annexes attached to this contract:"
        )
        + "</strong><br>"
        + _esc(c.annexes).replace("\n", "<br>")
        + "</div>"
        if c.annexes
        else ""
    )
    _add(
        (
            "LOI APPLICABLE ET DISPOSITION FINALE"
            if fr
            else "APPLICABLE LAW AND FINAL PROVISIONS"
        ),
        (
            f"""
        <p>Le pr\u00e9sent contrat est r\u00e9gi et interpr\u00e9t\u00e9 conform\u00e9ment au <strong>droit du Royaume du
        Maroc</strong>. Tout sujet non express\u00e9ment trait\u00e9 par le pr\u00e9sent contrat sera r\u00e9gi par les
        dispositions l\u00e9gales marocaines applicables, notamment le Dahir du 12 ao\u00fbt 1913 formant
        Code des Obligations et des Contrats (DOC).</p>
        <p>Le pr\u00e9sent contrat constitue l\u2019int\u00e9gralit\u00e9 de l\u2019accord entre les parties et annule et
        remplace tous les accords, n\u00e9gociations et propositions ant\u00e9rieurs relatifs \u00e0 son objet.</p>
        <p>Si l\u2019une des clauses du pr\u00e9sent contrat est d\u00e9clar\u00e9e nulle ou inapplicable, les autres
        clauses demeurent <strong>pleinement en vigueur</strong>.</p>
        {excl_extra}{spec_extra}{annex_extra}"""
            if fr
            else f"""
        <p>This contract is governed and interpreted in accordance with the <strong>laws of the Kingdom of Morocco</strong>. Any matter not expressly subject to this contract shall be governed by applicable Moroccan legal provisions, notably the Dahir of 12 August 1913 forming the Code of Obligations and Contracts (DOC).</p>
        <p>This contract constitutes the <strong>entire agreement</strong> between the parties and supersedes all prior agreements, negotiations and proposals relating to its subject matter.</p>
        <p>If any clause is declared void or unenforceable, the remaining clauses remain <strong>fully in force</strong>.</p>
        {excl_extra}{spec_extra}{annex_extra}"""
        ),
    )

    return articles


def _gen_contract_html(c, lang: str = "fr") -> str:
    fr = lang == "fr"
    confid_label = CONFID_LABELS.get(
        c.confidentialite or "confidentiel", "CONFIDENTIEL"
    )
    ctype_display = CTYPES_DISPLAY[lang].get(
        c.type_contrat or "travaux_finition", c.type_contrat or ""
    )
    date_str = _fmt_date(c.date_contrat)
    version_str = "v1.0 \u2013 D\u00e9finitif" if fr else "v1.0 \u2013 Final"
    ville = _esc(c.ville_signature) if c.ville_signature else "Tanger"
    ref = _esc(c.numero_contrat)

    client_nom = (
        _esc(c.client_nom)
        if c.client_nom
        else "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026"
    )
    client_cin = (
        _esc(c.client_cin)
        if c.client_cin
        else "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026"
    )
    client_qualite = QUALITE_LABELS[lang].get(
        c.client_qualite or "",
        c.client_qualite or ("Personne Physique" if fr else "Individual"),
    )
    client_adresse = (
        _esc(c.client_adresse)
        if c.client_adresse
        else "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026"
    )
    client_tel = (
        _esc(c.client_tel)
        if c.client_tel
        else "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026"
    )
    client_email = f"{_esc(c.client_email)}<br>" if c.client_email else ""
    sig_role = (
        ("Repr\u00e9sentant l\u00e9gal" if fr else "Legal Representative")
        if _is_societe(c.client_qualite)
        else ("Particulier" if fr else "Individual")
    )
    sig_name = (
        _esc(c.client_nom)
        if c.client_nom
        else "\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026\u2026"
    )

    resp_label = "Chef de projet" if fr else "Project Manager"
    resp_header = (
        f'<strong style="color:#888">{resp_label}\u202f:</strong> {_esc(c.responsable_projet)}'
        if c.responsable_projet
        else ""
    )

    articles = _build_articles(c, lang)
    arts_html = "\n".join(
        f'<div class="art">'
        f'<div class="art-title"><span class="anum">ART.&nbsp;{a["num"]}</span>{a["title"]}</div>'
        f'<div class="art-body">{a["body"]}</div>'
        f"</div>"
        for a in articles
    )

    # Bilingual labels
    lbl_date = "Date" if fr else "Date"
    lbl_version = "Version"
    lbl_classe = "Classe" if fr else "Class"
    confid_ribbon = (
        "DOCUMENT CONFIDENTIEL \u2013 USAGE EXCLUSIF DES PARTIES SIGNATAIRES"
        if fr
        else "CONFIDENTIAL DOCUMENT \u2013 FOR SIGNATORY PARTIES ONLY"
    )
    title_h1 = "CONTRAT DE PRESTATIONS DE SERVICES" if fr else "SERVICE AGREEMENT"
    between_txt = "ENTRE LES SOUSSIGN\u00c9S :" if fr else "BETWEEN THE UNDERSIGNED:"
    lbl_prest = "LE PRESTATAIRE" if fr else "THE SERVICE PROVIDER"
    lbl_client = "LE CLIENT" if fr else "THE CLIENT"
    ci_prest = (
        "Ci-apr\u00e8s d\u00e9nomm\u00e9e \u00ab Le Prestataire \u00bb"
        if fr
        else "Hereinafter referred to as \u00abThe Service Provider\u00bb"
    )
    ci_client = (
        "Ci-apr\u00e8s d\u00e9nomm\u00e9(e) \u00ab Le Client \u00bb"
        if fr
        else "Hereinafter referred to as \u00abThe Client\u00bb"
    )
    cin_label = "CIN / ICE" if fr else "ID / Passport"
    qualite_label = "Qualit\u00e9" if fr else "Status"
    sig_title = "\u270d SIGNATURES"
    sig_date = (
        f"Fait \u00e0 {ville}, le {date_str}"
        if fr
        else f"Done in {ville}, on {date_str}"
    )
    sig_note_client = (
        "Lu et approuv\u00e9 \u2013 Bon pour accord"
        if fr
        else "Read and approved \u2013 Agreement"
    )
    sig_note_prest = "Signature &amp; Cachet" if fr else "Signature &amp; Stamp"
    sig_direction = "Direction G\u00e9n\u00e9rale" if fr else "General Management"
    initials_txt = (
        "Paraphes des parties (chaque page)"
        if fr
        else "Initials of parties (each page)"
    )
    lbl_provider_init = "Prestataire" if fr else "Service Provider"

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <title>{"Contrat" if fr else "Contract"} {ref} \u2013 CASA DI LUSSO</title>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>{_PDF_CSS_TMPL.replace("__PAGE_SEP__", "sur" if fr else "of")}</style>
</head>
<body>

<div class="c-topstrip"></div>

<div class="c-header">
  <div class="c-header-left">
    <div class="c-logo">CASA DI <span class="cg">LUSSO</span></div>
    <div class="c-logo-tag">Design \u00b7 {"Travaux" if fr else "Works"} \u00b7 {"Ameublement" if fr else "Furnishing"} \u00b7 {"Maroc" if fr else "Morocco"}</div>
    <div class="c-logo-info">
      SARL \u00b7 RC 143377 \u00b7 ICE 003389356000001<br>
      IF 60116256 \u00b7 CNSS 5001474<br>
      Route N1, Al Moustakbal Roundabout \u2013 Tanger<br>
      {resp_header}
    </div>
  </div>
  <div class="c-header-right">
    <div class="c-ref">{ref}</div>
    <div class="c-date">
      <strong>{lbl_date}\u202f:</strong> {date_str}<br>
      <strong>{lbl_version}\u202f:</strong> {version_str}<br>
      <strong>{lbl_classe}\u202f:</strong> {confid_label}<br>
      {ville}, {"Maroc" if fr else "Morocco"}
    </div>
  </div>
</div>

<div class="c-confidential"><span>{confid_ribbon}</span></div>

<div class="c-title">
  <h1>{title_h1}</h1>
  <div class="c-subtitle">CASA DI LUSSO SARL \u00b7 RC 143377 \u00b7 Tanger, {"Maroc" if fr else "Morocco"}</div>
  <div class="c-type-badge">{ctype_display}</div>
</div>

<p class="c-between">{between_txt}</p>

<div class="c-parties">
  <div class="c-party prest">
    <div class="c-party-label">{lbl_prest}</div>
    <strong>CASA DI LUSSO SARL</strong><br>
    RC : 143377 \u00b7 ICE : 003389356000001<br>
    IF : 60116256 \u00b7 CNSS : 5001474<br>
    Route N1, Al Moustakbal Roundabout<br>
    Tanger \u2013 {"Maroc" if fr else "Morocco"}<br><br>
    <em>{ci_prest}</em>
  </div>
  <div class="c-party client">
    <div class="c-party-label">{lbl_client}</div>
    <strong>{client_nom}</strong><br>
    {cin_label} : {client_cin}<br>
    {qualite_label} : {client_qualite}<br>
    {client_adresse}<br>
    {client_tel}<br>
    {client_email}<br>
    <em>{ci_client}</em>
  </div>
</div>

{arts_html}

<div class="sigs-box">
  <div class="sigs-top">
    <div class="sigs-top-left"><div class="sigs-title">{sig_title}</div></div>
    <div class="sigs-top-right"><div class="sigs-date">{sig_date}</div></div>
  </div>
  <div class="sigs-grid">
    <div class="sig-box">
      <div class="sig-label">{lbl_client}</div>
      <div class="sig-note">{sig_note_client}</div>
      <div class="sig-line"></div>
      <div class="sig-name">{sig_name}</div>
      <div class="sig-role">{sig_role}</div>
    </div>
    <div class="sig-box">
      <div class="sig-label">CASA DI LUSSO SARL</div>
      <div class="sig-note">{sig_note_prest}</div>
      <div class="sig-line"></div>
      <div class="sig-name">{sig_direction}</div>
      <div class="sig-role">CASA DI LUSSO SARL</div>
    </div>
  </div>
  <div class="initials-row">
    <div class="init-box"><div class="init-line"></div><div class="init-label">Client</div></div>
    <div class="init-center">{initials_txt}</div>
    <div class="init-box"><div class="init-line"></div><div class="init-label">{lbl_provider_init}</div></div>
  </div>
</div>

<div class="c-footer">
  <div class="c-footer-logo">CASA DI LUSSO</div>
  <div class="c-footer-mid">{ref} \u00b7 RC 143377 \u00b7 Tanger, {"Maroc" if fr else "Morocco"}</div>
  <div class="c-footer-right">{version_str} \u00b7 {confid_label}</div>
</div>

</body>
</html>"""


class ContractPDFGenerator:
    """Generate a WeasyPrint PDF for a Contract instance."""

    def __init__(self, contract, language: str = "fr"):
        self.contract = contract
        self.language = language

    def generate_response(self) -> HttpResponse:
        import weasyprint  # lazy import – requires GTK on Windows

        html_content = _gen_contract_html(self.contract, self.language)
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()

        safe_ref = self.contract.numero_contrat.replace("/", "-")
        filename = f"contrat_{self.contract.id}_{safe_ref}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
