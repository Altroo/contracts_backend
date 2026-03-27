"""
contract/st_pdf.py
~~~~~~~~~~~~~~~~~~
Generates a full Sous-Traitance contract PDF using WeasyPrint + inline HTML/CSS.
Uses CDL branding (dark #0F0F1A + gold #B8973A, Cormorant Garamond + Inter fonts).
"""

from datetime import datetime

from django.http import HttpResponse
from weasyprint import HTML

from core.models import CompanyConfig
from .pdf import _fmt_date, _fmt_amt, _esc
from .st_i18n import (
    LOT_LABELS,
    LOT_NORMES,
    LOT_ASSURANCES,
    LOT_DESC_DEFAULT,
    LOT_OBLIGATIONS,
    LOT_RECEPTION,
    FORME_LABELS,
    TYPE_PRIX_LABELS,
    DELAI_UNIT_LABELS,
    st_t,
)

# ── helpers ─────────────────────────────────────────────────────────────────


def _resolve_lot_keys(lot_type) -> list:
    """Accept a str key, a list of str keys, or None; always return a list."""
    if not lot_type:
        return []
    if isinstance(lot_type, list):
        return [k for k in lot_type if k]
    return [lot_type]


def _resolve_type_prix_keys(type_prix) -> list:
    """Accept a str key, a list of str keys, or None; return a list (default forfaitaire)."""
    if not type_prix:
        return ["forfaitaire"]
    if isinstance(type_prix, list):
        return [k for k in type_prix if k] or ["forfaitaire"]
    return [type_prix]


def _num_to_words_mad(n: int, lang: str) -> str:
    """Convert integer n to words for the contract 'arrêté à la somme de' line."""
    try:
        from num2words import num2words  # type: ignore[import-untyped]

        locale = "fr" if lang == "fr" else "en"
        return num2words(n, lang=locale).capitalize()
    except Exception:  # ImportError or any num2words error
        return f"{n:,}".replace(",", "\u202f")


# ── CSS ──────────────────────────────────────────────────────────────────────

_ST_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

@page {
  size: A4;
  margin: 18mm 18mm 22mm 18mm;
  @bottom-center {
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 7pt; color: #ccc;
    content: "Page " counter(page) " sur " counter(pages);
  }
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Inter', Arial, Helvetica, sans-serif;
  font-size: 9pt; color: #1C1C2E; background: #fff; line-height: 1.75;
}

/* ── top strip ── */
.st-topstrip {
  height: 4px;
  background: linear-gradient(90deg, #0F0F1A 0%, #B8973A 50%, #0F0F1A 100%);
  margin-bottom: 20pt;
}

/* ── header ── */
.st-header { display: table; width: 100%; padding-bottom: 14pt; border-bottom: 0.5pt solid #E2D9C8; margin-bottom: 16pt; }
.st-header-left { display: table-cell; vertical-align: top; }
.st-header-right { display: table-cell; vertical-align: top; text-align: right; }
.st-logo { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 20pt; font-weight: 700; letter-spacing: 2px; color: #0F0F1A; line-height: 1; }
.st-logo .cg { color: #B8973A; }
.st-logo-tag { font-size: 7.5pt; color: #999; letter-spacing: 2px; text-transform: uppercase; margin-top: 3pt; }
.st-logo-info { font-size: 7pt; color: #bbb; line-height: 1.8; margin-top: 5pt; }
.st-ref { font-family: 'JetBrains Mono', 'Courier New', monospace; background: #0F0F1A; color: #B8973A; padding: 3pt 9pt; font-size: 9pt; font-weight: 600; letter-spacing: 1px; display: inline-block; margin-bottom: 6pt; border-radius: 3pt; }
.st-date { font-size: 8pt; color: #888; line-height: 1.9; }
.st-date strong { color: #1C1C2E; font-weight: 600; }

/* ── title block ── */
.st-title { text-align: center; margin: 0 0 16pt; padding: 14pt 0 12pt; border-top: 1pt solid #eee; border-bottom: 1pt solid #eee; position: relative; }
.st-title::before { content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 40pt; height: 3pt; background: #B8973A; border-radius: 0 0 2pt 2pt; }
.st-title h1 { font-family: 'Cormorant Garamond', Georgia, serif; font-size: 14pt; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; color: #0F0F1A; margin-bottom: 4pt; }
.st-subtitle { font-size: 8pt; color: #aaa; letter-spacing: 1.5px; text-transform: uppercase; }
.st-badge { display: inline-block; margin-top: 6pt; background: #F7F0E0; border: 1pt solid #B8973A; color: #B8973A; padding: 2pt 10pt; font-size: 7.5pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; border-radius: 10pt; }

/* ── parties ── */
.st-between { font-size: 9pt; font-weight: 600; color: #666; margin-bottom: 8pt; font-style: italic; }
.st-parties { display: table; width: 100%; margin-bottom: 16pt; border-spacing: 8pt 0; }
.st-party { display: table-cell; width: 50%; padding: 10pt 12pt; vertical-align: top; font-size: 8.5pt; line-height: 1.85; }
.st-party.ep { background: #0F0F1A; color: rgba(255,255,255,0.85); border-radius: 4pt; }
.st-party.sub { background: #FAF6EC; border: 1pt solid #B8973A; border-radius: 4pt; }
.st-party-label { font-size: 7pt; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: #B8973A; padding-bottom: 5pt; margin-bottom: 6pt; }
.st-party.ep .st-party-label { border-bottom: 0.5pt solid rgba(184,151,58,0.3); }
.st-party.sub .st-party-label { border-bottom: 0.5pt solid #B8973A; }
.st-party.ep strong { color: #fff; }
.st-party.sub strong { color: #0F0F1A; }
.st-party em { font-size: 8pt; opacity: 0.7; font-style: italic; }
.st-together { text-align: center; font-style: italic; font-size: 8.5pt; color: #555; margin: 4pt 0 12pt; }

/* ── articles ── */
.st-art { margin-bottom: 11pt; page-break-inside: avoid; }
.st-art-title { font-size: 8pt; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; color: #0F0F1A; background: #F7F0E0; border-left: 3pt solid #B8973A; padding: 5pt 10pt 5pt 12pt; margin-bottom: 6pt; border-radius: 0 4pt 4pt 0; }
.st-art-title .anum { font-family: 'JetBrains Mono', 'Courier New', monospace; font-size: 8px; color: #B8973A; background: #0F0F1A; padding: 3pt 6pt; border-radius: 3pt; letter-spacing: 0; margin-right: 6pt; }
.st-art-body { font-size: 8.5pt; color: #222; padding: 0 4pt; line-height: 1.8; }
.st-art-body p { margin-bottom: 4pt; }
.st-art-body ul { padding-left: 15pt; margin: 3pt 0; }
.st-art-body li { margin-bottom: 2pt; }
.st-art-body table { width: 100%; border-collapse: collapse; font-size: 8.5pt; margin: 6pt 0; }
.st-art-body table th { background: #0F0F1A; color: #B8973A; padding: 5pt 8pt; text-align: left; font-size: 7pt; font-weight: 600; letter-spacing: 0.5px; }
.st-art-body table td { padding: 5pt 8pt; border-bottom: 0.5pt solid #eee; }
.st-art-body table tr:nth-child(even) td { background: rgba(247,240,224,0.3); }
.st-art-sub { font-size: 8.5pt; font-weight: 600; color: #0F0F1A; margin: 8pt 0 4pt; }

/* ── financial summary ── */
.st-fin-box { background: #FAF6EC; border: 1pt solid #E2D9C8; padding: 10pt 14pt; border-radius: 6pt; margin: 8pt 0; }
.st-fin-row { display: table; width: 100%; padding: 3pt 0; font-size: 8.5pt; border-bottom: 0.5pt solid #E2D9C8; }
.st-fin-row .lbl { display: table-cell; }
.st-fin-row .val { display: table-cell; text-align: right; font-weight: 600; }
.st-fin-row.grand { border-bottom: none; border-top: 2pt solid #0F0F1A; margin-top: 4pt; padding-top: 8pt; font-size: 11pt; font-weight: 700; color: #0F0F1A; }
.st-fin-row.grand .val { color: #B8973A; }
.st-fin-row.arrete { border-bottom: none; font-size: 8pt; color: #666; font-style: italic; padding-top: 4pt; }

/* ── payment tranches ── */
.st-ech-grid { display: table; width: 100%; margin: 8pt 0; border-spacing: 6pt 0; }
.st-ech { display: table-cell; padding: 8pt; border: 1pt solid #E2D9C8; border-radius: 6pt; vertical-align: top; background: rgba(247,240,224,0.2); }
.st-ech-label { font-size: 7pt; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #999; margin-bottom: 3pt; }
.st-ech-amount { font-size: 12pt; font-weight: 700; color: #0F0F1A; }
.st-ech-detail { font-size: 7pt; color: #999; margin-top: 2pt; }

/* ── signatures ── */
.st-sig-box { margin-top: 18pt; border-top: 1.5pt solid #E2D9C8; padding-top: 14pt; page-break-inside: avoid; }
.st-sig-info { font-size: 8.5pt; padding: 8pt 12pt; background: rgba(247,240,224,0.4); border: 0.5pt solid #E2D9C8; border-radius: 4pt; margin-bottom: 12pt; }
.st-sigs { display: table; width: 100%; border-spacing: 12pt 0; }
.st-sig { display: table-cell; width: 50%; border: 1pt solid #E2D9C8; padding: 10pt; vertical-align: top; border-radius: 4pt; }
.st-sig-label { font-size: 7pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #B8973A; margin-bottom: 3pt; }
.st-sig-note { font-size: 8pt; color: #888; margin-bottom: 6pt; font-style: italic; }
.st-sig-line { border-bottom: 0.5pt dashed #ccc; height: 40pt; margin-bottom: 6pt; }
.st-sig-name { font-size: 8.5pt; font-weight: 600; color: #0F0F1A; }
.st-sig-role { font-size: 7.5pt; color: #888; }

/* ── annexe table ── */
.st-annex-table { width: 100%; border-collapse: collapse; font-size: 8.5pt; margin: 6pt 0; }
.st-annex-table th { background: #0F0F1A; color: #B8973A; padding: 5pt 8pt; text-align: left; font-size: 7pt; font-weight: 600; }
.st-annex-table th.chk { width: 40pt; text-align: center; }
.st-annex-table td { padding: 5pt 8pt; border-bottom: 0.5pt solid #eee; }
.st-annex-table td.chk { text-align: center; font-size: 10pt; }
.st-annex-table tr:nth-child(even) td { background: rgba(247,240,224,0.3); }

/* ── paraphes row ── */
.st-paraphes { margin-top: 14pt; font-size: 7.5pt; color: #999; text-align: center; font-style: italic; }

/* ── footer ── */
.st-footer { margin-top: 12pt; padding-top: 7pt; border-top: 0.5pt solid #E2D9C8; text-align: center; font-size: 7pt; color: #aaa; line-height: 1.8; }
.st-footer strong { color: #0F0F1A; }
"""


class SousTraitancePDFGenerator:
    """Generate a WeasyPrint PDF for a Sous-Traitance contract."""

    def __init__(self, contract, language: str = "fr"):
        self.c = contract
        self.lang = language
        self.fr = language == "fr"
        self._ep = None  # lazily loaded CompanyConfig
        self._art_num = 0

    # ── helpers ───────────────────────────────────────────────────────────────

    def _t(self, key: str) -> str:
        return st_t(key, self.lang)

    def _tx(self, key: str) -> str:
        """Return a translation value that might be a list; returns str."""
        val = st_t(key, self.lang)
        if isinstance(val, list):
            return val[0] if val else ""
        return val

    def _next_art(self) -> int:
        self._art_num += 1
        return self._art_num

    def _art(self, title: str, body: str) -> str:
        n = self._next_art()
        return f"""
        <div class="st-art">
          <div class="st-art-title"><span class="anum">{n:02d}</span> {_esc(title)}</div>
          <div class="st-art-body">{body}</div>
        </div>"""

    @property
    def ep(self):
        if self._ep is None:
            try:
                self._ep = CompanyConfig.objects.get(company=self.c.company)
            except CompanyConfig.DoesNotExist:
                self._ep = None
        return self._ep

    @property
    def _ht(self) -> float:
        try:
            return float(self.c.montant_ht or 0)
        except (TypeError, ValueError):
            return 0.0

    @property
    def _tva_pct(self) -> float:
        try:
            return float(self.c.tva if self.c.tva is not None else 20)
        except (TypeError, ValueError):
            return 20.0

    @property
    def _tva_amt(self) -> float:
        return self._ht * self._tva_pct / 100

    @property
    def _ttc(self) -> float:
        return self._ht + self._tva_amt

    def _dev(self) -> str:
        return self.c.devise or "MAD"

    def _lot(self) -> str:
        lot_keys = _resolve_lot_keys(self.c.st_lot_type)
        labels = LOT_LABELS.get(self.lang, LOT_LABELS["fr"])
        return " / ".join(labels.get(k, k) for k in lot_keys)

    # ── section builders ─────────────────────────────────────────────────────

    def _build_header(self) -> str:
        ep = self.ep
        ep_name = _esc(ep.name) if ep else "CASA DI LUSSO"
        ep_rc = _esc(ep.rc) if ep else ""
        ep_ice = _esc(ep.ice) if ep else ""
        ep_addr = _esc(ep.adresse) if ep else ""
        ref = _esc(self.c.numero_contrat or "")
        date_str = _fmt_date(self.c.date_contrat)
        projet_name = ""
        if self.c.st_projet:
            projet_name = _esc(self.c.st_projet.name)
        return f"""
        <div class="st-header">
          <div class="st-header-left">
            <div class="st-logo">CASA <span class="cg">DI LUSSO</span></div>
            <div class="st-logo-tag">ENTREPRENEUR PRINCIPAL</div>
            <div class="st-logo-info">
              {ep_name}<br>
              RC {ep_rc} · ICE {ep_ice}<br>
              {ep_addr}
            </div>
          </div>
          <div class="st-header-right">
            <div class="st-ref">{self._t('ref')} {ref}</div><br>
            <div class="st-date"><strong>{self._t('date_label')}</strong> {date_str}</div>
            {f'<div class="st-date"><strong>{self._t("projet")} :</strong> {projet_name}</div>' if projet_name else ''}
          </div>
        </div>"""

    def _build_title(self) -> str:
        lot_label = self._lot()
        return f"""
        <div class="st-title">
          <h1>{self._t('contrat_title')}</h1>
          <div class="st-subtitle">{self._t('preamble')}</div>
          {f'<div class="st-badge">{_esc(lot_label)}</div>' if lot_label else ''}
        </div>"""

    def _build_parties(self) -> str:
        ep = self.ep
        c = self.c
        lang = self.lang
        t = self._t

        # EP info
        ep_name = _esc(ep.name) if ep else "CASA DI LUSSO SARL"
        ep_forme = _esc(ep.forme_juridique) if ep else "SARL"
        ep_capital = _fmt_amt(ep.capital, self._dev()) if ep and ep.capital else "—"
        ep_rc = _esc(ep.rc) if ep else "—"
        ep_ice = _esc(ep.ice) if ep else "—"
        ep_if = _esc(ep.identifiant_fiscal) if ep else "—"
        ep_addr = _esc(ep.adresse) if ep else "—"
        ep_rep = _esc(ep.representant) if ep else "—"
        ep_qualite = _esc(ep.qualite_representant) if ep else "Gérant"

        # ST info
        st_name = _esc(c.st_name or "—")
        st_forme_key = c.st_forme or ""
        st_forme_lbl = FORME_LABELS.get(lang, FORME_LABELS["fr"]).get(
            st_forme_key, st_forme_key
        )
        st_capital = _fmt_amt(c.st_capital, self._dev()) if c.st_capital else "—"
        st_rc = _esc(c.st_rc or "—")
        st_ice = _esc(c.st_ice or "—")
        st_if = _esc(c.st_if or "—")
        st_cnss = _esc(c.st_cnss or "—")
        st_addr = _esc(c.st_addr or "—")
        st_rep = _esc(c.st_rep or "—")
        st_cin = _esc(c.st_cin or "—")
        st_qualite = _esc(c.st_qualite or "—")
        st_tel = _esc(c.st_tel or "—")
        st_email = _esc(c.st_email or "—")
        st_rib = _esc(c.st_rib or "—")
        st_banque = _esc(c.st_banque or "—")

        return f"""
        <div class="st-between">{t('entre')}</div>
        <div class="st-parties">
          <div class="st-party ep">
            <div class="st-party-label">{t('lbl_ep')}</div>
            <strong>{ep_name}</strong><br>
            {t('forme_juridique')} : {ep_forme}<br>
            {t('capital_social')} : {ep_capital}<br>
            {t('rc')} : {ep_rc}<br>
            {t('ice')} : {ep_ice}<br>
            {t('if_label')} : {ep_if}<br>
            {t('siege')} : {ep_addr}<br>
            {t('representant')} : {ep_rep}<br>
            {t('qualite')} : {ep_qualite}<br>
            <em>{t('ci_ep')}</em>
          </div>
          <div class="st-party sub">
            <div class="st-party-label">{t('lbl_st')}</div>
            <strong>{st_name}</strong><br>
            {t('forme_juridique')} : {st_forme_lbl}<br>
            {t('capital_social')} : {st_capital}<br>
            {t('rc')} : {st_rc}<br>
            {t('ice')} : {st_ice}<br>
            {t('if_label')} : {st_if}<br>
            {t('cnss')} : {st_cnss}<br>
            {t('siege')} : {st_addr}<br>
            {t('representant')} : {st_rep}<br>
            {t('cin')} : {st_cin}<br>
            {t('qualite')} : {st_qualite}<br>
            {t('telephone')} : {st_tel}<br>
            {t('email')} : {st_email}<br>
            {t('rib')} : {st_rib}<br>
            {t('banque')} : {st_banque}<br>
            <em>{t('ci_st')}</em>
          </div>
        </div>
        <p class="st-together">{t('parties_ensemble')}</p>"""

    # ── Article builders ─────────────────────────────────────────────────────

    def _build_art_parties(self) -> str:
        """Article 1 – Parties (already built visually above, article just references)."""
        t = self._t
        body = f"""
        <p class="st-art-sub">{t('partie_ep_title')}</p>
        <p>{t('ci_ep')}</p>
        <p class="st-art-sub">{t('partie_st_title')}</p>
        <p>{t('ci_st')}</p>"""
        return self._art(t("art_parties"), body)

    def _build_art_objet(self) -> str:
        """Article 2 – Objet du contrat."""
        t = self._t
        c = self.c
        lang = self.lang
        lot_keys = _resolve_lot_keys(c.st_lot_type)
        lot_key = lot_keys[0] if lot_keys else ""
        lot_label = " / ".join(
            LOT_LABELS.get(lang, LOT_LABELS["fr"]).get(k, k) for k in lot_keys
        )
        lot_desc = c.st_lot_description or LOT_DESC_DEFAULT.get(
            lang, LOT_DESC_DEFAULT["fr"]
        ).get(lot_key, "")
        normes = LOT_NORMES.get(lot_key, "")

        projet = c.st_projet
        proj_name = _esc(projet.name) if projet else "—"
        proj_addr = _esc(projet.adresse) if projet and projet.adresse else "—"
        proj_mo = (
            _esc(projet.maitre_ouvrage) if projet and projet.maitre_ouvrage else "—"
        )
        proj_permis = _esc(projet.permis) if projet and projet.permis else "—"

        body = f"""
        <p>{t('objet_intro')}</p>
        <p><strong>{_esc(lot_label)}</strong></p>
        <p>{_esc(lot_desc)}</p>
        <table>
          <tr><td style="width:35%;font-weight:600;">{t('objet_projet')}</td><td>{proj_name}</td></tr>
          <tr><td style="font-weight:600;">{t('objet_adresse')}</td><td>{proj_addr}</td></tr>
          <tr><td style="font-weight:600;">{t('objet_mo')}</td><td>{proj_mo}</td></tr>
          <tr><td style="font-weight:600;">{t('objet_permis')}</td><td>{proj_permis}</td></tr>
          <tr><td style="font-weight:600;">{t('objet_normes')}</td><td>{_esc(normes)}</td></tr>
        </table>
        <p>{t('objet_declaration')}</p>"""
        return self._art(t("art_objet"), body)

    def _build_art_docs(self) -> str:
        """Article 3 – Documents contractuels."""
        t = self._t
        lot_keys = _resolve_lot_keys(self.c.st_lot_type)
        lot_key = lot_keys[0] if lot_keys else ""
        normes = LOT_NORMES.get(lot_key, "")
        docs = st_t("docs_list", self.lang)
        if isinstance(docs, list):
            parts = []
            for idx, d in enumerate(docs):
                text = f"{d} : {normes}" if idx == 6 and normes else d
                parts.append(f"<li>{_esc(text)}</li>")
            items = "".join(parts)
        else:
            items = ""
        body = (
            f"<p>{t('docs_intro')}</p><ol>{items}</ol><p>{t('docs_contradiction')}</p>"
        )
        return self._art(t("art_docs"), body)

    def _build_art_prix(self) -> str:
        """Article 4 – Prix et conditions financières."""
        t = self._t
        c = self.c
        lang = self.lang
        dev = self._dev()

        type_prix_keys = _resolve_type_prix_keys(c.st_type_prix)
        type_prix_lbl = " / ".join(
            TYPE_PRIX_LABELS.get(lang, TYPE_PRIX_LABELS["fr"]).get(k, k)
            for k in type_prix_keys
        )

        tva_pct = self._tva_pct
        ht_str = _fmt_amt(self._ht, dev)
        tva_str = _fmt_amt(self._tva_amt, dev)
        ttc_str = _fmt_amt(self._ttc, dev)

        body = f"""
        <p class="st-art-sub">{t('prix_montant')}</p>
        <p>{t('prix_type')} <strong>{_esc(type_prix_lbl)}</strong></p>
        <div class="st-fin-box">
          <div class="st-fin-row"><span class="lbl">{t('prix_ht')}</span><span class="val">{ht_str}</span></div>
          <div class="st-fin-row"><span class="lbl">{t('prix_tva').format(tva=f'{tva_pct:g}')}</span><span class="val">{tva_str}</span></div>
          <div class="st-fin-row grand"><span class="lbl">{t('prix_ttc')}</span><span class="val">{ttc_str}</span></div>
          <div class="st-fin-row arrete"><span class="lbl">{t('prix_arrete')}</span><span class="val">{_esc(_num_to_words_mad(round(self._ttc), lang))} {dev}.</span></div>
        </div>
        <p>{t('prix_comprend')}</p>"""

        # Payment terms
        delai_pay = c.st_delai_paiement or 30
        rib_info = ""
        if c.st_rib or c.st_banque:
            if self.lang == "fr":
                rib_info = f" sur le compte n\u00b0\u00a0{_esc(c.st_rib or '\u2014')} ouvert aupr\u00e8s de {_esc(c.st_banque or '\u2014')}"
            else:
                rib_info = f" on account n\u00b0\u00a0{_esc(c.st_rib or '\u2014')} held at {_esc(c.st_banque or '\u2014')}"
        body += f"""
        <p class="st-art-sub">{t('prix_modalites')}</p>
        <p>{t('prix_virement_intro').format(rib_info=rib_info)}</p>
        <p>{t('prix_delai_paiement').format(days=delai_pay)}</p>"""

        # Tranches
        tranches = c.st_tranches or []
        if tranches:
            body += '<div class="st-ech-grid">'
            for i, tr in enumerate(tranches):
                lbl = _esc(tr.get("label", f"Tranche {i+1}"))
                pct = float(tr.get("pourcentage", 0))
                amt = self._ht * pct / 100
                body += f"""
                <div class="st-ech">
                  <div class="st-ech-label">{lbl}</div>
                  <div class="st-ech-amount">{_fmt_amt(amt, dev)}</div>
                  <div class="st-ech-detail">{pct:g}%</div>
                </div>"""
            body += "</div>"

        # Avance
        avance_pct = float(c.st_avance or 0)
        if avance_pct > 0:
            avance_amt = self._ht * avance_pct / 100
            body += f"""
            <p class="st-art-sub">{t('prix_avance')}</p>
            <p>{t('prix_avance_text').format(pct=f'{avance_pct:g}', amount=_fmt_amt(avance_amt, dev))}</p>"""

        # Retenue de garantie
        ret_pct = float(c.st_retenue_garantie or 0)
        garantie_ret_mois = c.st_garantie_mois or 12
        if ret_pct > 0:
            body += f"""
            <p class="st-art-sub">{t('prix_retenue')}</p>
            <p>{t('prix_retenue_text').format(pct=f'{ret_pct:g}', months=garantie_ret_mois)}</p>"""

        # Travaux supplémentaires
        body += f"""
        <p class="st-art-sub">{t('prix_supplementaires')}</p>
        <p>{t('prix_supplementaires_text')}</p>"""

        return self._art(t("art_prix"), body)

    def _build_art_delais(self) -> str:
        """Article 5 – Délais d'exécution."""
        t = self._t
        c = self.c
        lang = self.lang
        val = c.st_delai_val or "—"
        unit_key = c.st_delai_unit or "mois"
        unit_lbl = DELAI_UNIT_LABELS.get(lang, DELAI_UNIT_LABELS["fr"]).get(
            unit_key, unit_key
        )
        pen_taux = c.st_penalite_taux or 1
        plafond = c.st_plafond_penalite or 10

        body = f"""
        <p class="st-art-sub">{t('delais_global')}</p>
        <p>{t('delais_global_text').format(val=val, unit=unit_lbl)}</p>
        <p class="st-art-sub">{t('delais_planning')}</p>
        <p>{t('delais_planning_text')}</p>
        <p class="st-art-sub">{t('delais_penalites')}</p>
        <p>{t('delais_penalites_text').format(taux=f'{float(pen_taux):g}', plafond=f'{float(plafond):g}')}</p>
        <p class="st-art-sub">{t('delais_resiliation')}</p>
        <p>{t('delais_resiliation_text')}</p>"""
        return self._art(t("art_delais"), body)

    def _build_art_obligations_st(self) -> str:
        """Article 6 – Obligations du ST."""
        t = self._t
        lang = self.lang
        lot_keys = _resolve_lot_keys(self.c.st_lot_type)
        lot_key = lot_keys[0] if lot_keys else ""

        # General
        gen_items = st_t("oblig_generales_list", lang)
        gen_html = (
            "".join(f"<li>{_esc(i)}</li>" for i in gen_items)
            if isinstance(gen_items, list)
            else ""
        )

        body = f"""
        <p class="st-art-sub">{t('oblig_generales')}</p>
        <ul>{gen_html}</ul>"""

        # Specific
        specific = LOT_OBLIGATIONS.get(lang, LOT_OBLIGATIONS["fr"]).get(lot_key, [])
        if specific:
            spec_html = "".join(f"<li>{_esc(o)}</li>" for o in specific)
            body += f"""
            <p class="st-art-sub">{t('oblig_specifiques')}</p>
            <ul>{spec_html}</ul>"""

        return self._art(t("art_obligations_st"), body)

    def _build_art_obligations_ep(self) -> str:
        """Article 7 – Obligations de l'EP."""
        t = self._t
        items = st_t("oblig_ep_list", self.lang)
        items_html = (
            "".join(f"<li>{_esc(i)}</li>" for i in items)
            if isinstance(items, list)
            else ""
        )
        body = f"<ul>{items_html}</ul>"
        return self._art(t("art_obligations_ep"), body)

    def _build_art_assurances(self) -> str:
        """Article 8 – Assurances."""
        t = self._t
        lang = self.lang
        lot_keys = _resolve_lot_keys(self.c.st_lot_type)
        lot_key = lot_keys[0] if lot_keys else ""
        lot_assur = LOT_ASSURANCES.get(lang, LOT_ASSURANCES["fr"]).get(lot_key, "")

        body = f"<p>{t('assurances_intro')}</p>"
        if lot_assur:
            body += f"<p><strong>{_esc(lot_assur)}</strong></p>"

        rules = st_t("assurances_rules", lang)
        if isinstance(rules, list):
            body += "<ul>" + "".join(f"<li>{_esc(r)}</li>" for r in rules) + "</ul>"

        actives = self.c.st_clauses_actives or []
        if "tTRC" in actives:
            body += f"<p>{t('assurances_trc')}</p>"
        return self._art(t("art_assurances"), body)

    def _build_art_reception(self) -> str:
        """Article 9 – Réception des travaux."""
        t = self._t
        lang = self.lang
        c = self.c
        lot_keys = _resolve_lot_keys(c.st_lot_type)
        lot_key = lot_keys[0] if lot_keys else ""
        reception_text = LOT_RECEPTION.get(lang, LOT_RECEPTION["fr"]).get(lot_key, "")
        delai_res = c.st_delai_reserves or 30
        garantie_mois = c.st_garantie_mois or 12

        body = f"""
        <p class="st-art-sub">{t('reception_provisoire')}</p>
        <p>{t('reception_provisoire_text')}</p>
        <p>{_esc(reception_text)}</p>
        <p>{t('reception_pv_text')}</p>
        <p class="st-art-sub">{t('reception_reserves')}</p>
        <p>{t('reception_reserves_text').format(days=delai_res)}</p>
        <p class="st-art-sub">{t('reception_definitive')}</p>
        <p>{t('reception_definitive_text').format(months=garantie_mois)}</p>
        <p class="st-art-sub">{t('reception_decennale')}</p>
        <p>{t('reception_decennale_text')}</p>"""
        return self._art(t("art_reception"), body)

    def _build_art_responsabilite(self) -> str:
        """Article 10 – Responsabilité et garanties."""
        t = self._t
        c = self.c
        body = f"""
        <p>{t('resp_resultat')}</p>
        <p>{t('resp_recours')}</p>
        <p>{t('resp_personnel')}</p>
        <p>{t('resp_defaillance').format(days=c.st_delai_med or 8)}</p>"""
        return self._art(t("art_responsabilite"), body)

    def _build_art_resiliation(self) -> str:
        """Article 11 – Résiliation."""
        t = self._t
        c = self.c
        delai_med = c.st_delai_med or 8
        items = st_t("resil_faute_list", self.lang)
        items_html = (
            "".join(f"<li>{_esc(i)}</li>" for i in items)
            if isinstance(items, list)
            else ""
        )
        body = f"""
        <p class="st-art-sub">{t('resil_faute')}</p>
        <p>{t('resil_faute_intro')}</p>
        <ul>{items_html}</ul>
        <p>{t('resil_faute_effet').format(days=delai_med)}</p>
        <p class="st-art-sub">{t('resil_convenance')}</p>
        <p>{t('resil_convenance_text')}</p>
        <p class="st-art-sub">{t('resil_consequences')}</p>
        <p>{t('resil_consequences_text')}</p>"""
        return self._art(t("art_resiliation"), body)

    def _build_art_hse(self) -> str:
        """Article 12 – Hygiène, Sécurité et Environnement."""
        t = self._t
        items = st_t("hse_list", self.lang)
        items_html = (
            "".join(f"<p>{_esc(i)}</p>" for i in items)
            if isinstance(items, list)
            else ""
        )
        return self._art(t("art_hse"), items_html)

    def _build_optional_clauses(self) -> str:
        """Build articles for each active optional clause."""
        actives = self.c.st_clauses_actives or []
        html = ""
        projet = self.c.st_projet
        mo = _esc(
            projet.maitre_ouvrage
            if projet and projet.maitre_ouvrage
            else ("le Maître d'Ouvrage" if self.fr else "the Employer")
        )
        clause_confid_amount = _fmt_amt(self._ht * 0.2, self._dev())

        if "tConfid" in actives:
            n = self._art_num + 1
            if self.fr:
                body = (
                    f"<p><strong>{n}.1.</strong> Le Sous-Traitant s'engage à traiter comme strictement confidentielles toutes les informations techniques, commerciales et financières dont il pourrait avoir connaissance dans le cadre de l'exécution du présent contrat.</p>"
                    f"<p><strong>{n}.2.</strong> Cette obligation de confidentialité s'étend au personnel du Sous-Traitant et à tout tiers auquel il pourrait faire appel. Elle survit à l'extinction du contrat pour une durée de <strong>3 ans</strong>.</p>"
                    f"<p><strong>{n}.3.</strong> Toute violation de cette clause expose le Sous-Traitant au paiement d'une indemnité forfaitaire de <strong>{clause_confid_amount}</strong>, sans préjudice du droit de l'Entrepreneur Principal à demander réparation du préjudice réel subi.</p>"
                )
            else:
                body = (
                    f"<p><strong>{n}.1.</strong> The Subcontractor undertakes to treat as strictly confidential all technical, commercial and financial information that may come to its knowledge in the performance of this contract.</p>"
                    f"<p><strong>{n}.2.</strong> This confidentiality obligation extends to the Subcontractor's personnel and to any third party it may engage. It survives termination of the contract for a period of <strong>3 years</strong>.</p>"
                    f"<p><strong>{n}.3.</strong> Any breach of this clause exposes the Subcontractor to a lump-sum indemnity of <strong>{clause_confid_amount}</strong>, without prejudice to the Principal Contractor's right to claim compensation for the actual loss suffered.</p>"
                )
            html += self._art(self._t("clause_confid"), body)

        if "tNonConc" in actives:
            if self.fr:
                body = (
                    f"<p>Le Sous-Traitant s'interdit, pendant toute la durée du contrat et pendant une période de <strong>12 mois</strong> suivant son terme, de contracter directement avec le Maître d'Ouvrage <strong>{mo}</strong> ou avec tout acquéreur des lots du projet, pour des prestations similaires à celles objet du présent contrat, dans un rayon de <strong>20 km</strong> autour du projet.</p>"
                    "<p>Toute violation expose le Sous-Traitant au paiement d'une indemnité forfaitaire de <strong>30%</strong> du montant HT du présent contrat.</p>"
                )
            else:
                body = (
                    f"<p>The Subcontractor undertakes, throughout the term of the contract and for a period of <strong>12 months</strong> after its expiry, not to contract directly with the Employer <strong>{mo}</strong> or with any purchaser of lots in the project for services similar to those covered by this contract, within a radius of <strong>20 km</strong> around the project.</p>"
                    "<p>Any breach exposes the Subcontractor to a lump-sum indemnity equal to <strong>30%</strong> of the pre-tax amount of this contract.</p>"
                )
            html += self._art(self._t("clause_non_conc"), body)

        if "tNonDeb" in actives:
            html += self._art(
                self._t("clause_non_deb"),
                (
                    "<p>Chacune des Parties s'interdit de recruter ou de tenter de recruter, directement ou indirectement, tout salarié ou collaborateur de l'autre Partie ayant participé à l'exécution du présent contrat, pendant toute la durée du contrat et pendant une période de <strong>12 mois</strong> suivant son terme.</p>"
                    "<p>Toute violation entraînera le paiement d'une indemnité forfaitaire équivalente à <strong>12 mois</strong> de rémunération brute du salarié concerné.</p>"
                    if self.fr
                    else "<p>Each Party undertakes not to recruit or attempt to recruit, directly or indirectly, any employee or collaborator of the other Party who has participated in the performance of this contract, throughout the term of the contract and for a period of <strong>12 months</strong> after its expiry.</p><p>Any breach shall result in a lump-sum indemnity equal to <strong>12 months</strong> of the gross remuneration of the employee concerned.</p>"
                ),
            )

        if "tCascade" in actives:
            html += self._art(
                self._t("clause_cascade"),
                (
                    "<p>Le Sous-Traitant s'interdit formellement de sous-traiter tout ou partie des travaux objets du présent contrat à un tiers, sauf accord écrit et préalable de l'Entrepreneur Principal.</p><p>En cas de violation, l'Entrepreneur Principal pourra résilier immédiatement le contrat aux torts exclusifs du Sous-Traitant, sans mise en demeure préalable, et sans préjudice de dommages et intérêts.</p>"
                    if self.fr
                    else "<p>The Subcontractor is formally prohibited from subcontracting all or part of the works covered by this contract to a third party unless it has obtained the Principal Contractor's prior written consent.</p><p>In the event of breach, the Principal Contractor may terminate the contract immediately at the Subcontractor's sole fault, without prior notice and without prejudice to damages.</p>"
                ),
            )

        if "tEnviro" in actives:
            html += self._art(
                self._t("clause_enviro"),
                (
                    "<p>Le Sous-Traitant s'engage à respecter la législation environnementale en vigueur au Maroc, notamment la loi n° 11-03 relative à la protection et à la mise en valeur de l'environnement. Il s'engage à :</p><ul><li>Gérer ses déchets de chantier de manière responsable et les évacuer vers les décharges autorisées</li><li>Limiter les nuisances sonores et les émissions de poussière</li><li>Utiliser des matériaux respectueux de l'environnement dans la mesure du possible</li><li>Respecter les horaires de chantier pour limiter les nuisances au voisinage</li></ul>"
                    if self.fr
                    else "<p>The Subcontractor undertakes to comply with environmental legislation in force in Morocco, in particular Law No. 11-03 on environmental protection and enhancement. It undertakes to:</p><ul><li>Manage site waste responsibly and remove it to authorised dumps</li><li>Limit noise nuisance and dust emissions</li><li>Use environmentally friendly materials wherever possible</li><li>Respect site working hours in order to limit disturbance to neighbouring properties</li></ul>"
                ),
            )

        for toggle_key, title_key, text_key in [
            ("tPI", "clause_pi", "clause_pi_text"),
            ("tExclus", "clause_exclus", "clause_exclus_text"),
            ("tRevision", "clause_revision", "clause_revision_text"),
        ]:
            if toggle_key in actives:
                html += self._art(self._t(title_key), f"<p>{self._t(text_key)}</p>")
        return html

    def _build_trailing_articles(self) -> str:
        """Litiges, Force Majeure, Dispositions Générales."""
        t = self._t
        c = self.c
        html = ""

        # Médiation (optional clause toggle)
        actives = c.st_clauses_actives or []
        if "tMediat" in actives:
            med_body = f"""
            <p>{t('litiges_mediation')}</p>
            <p>{t('litiges_tribunal_mediation')}</p>"""
        else:
            med_body = f"<p>{t('litiges_tribunal')}</p>"
        html += self._art(t("art_litiges"), med_body)

        # Force majeure
        html += self._art(t("art_force_majeure"), f"<p>{t('force_majeure_text')}</p>")

        # Dispositions générales
        items = st_t("dispositions_items", self.lang)
        items_html = (
            "".join(f"<li>{_esc(i)}</li>" for i in items)
            if isinstance(items, list)
            else ""
        )
        html += self._art(t("art_dispositions"), f"<ul>{items_html}</ul>")

        return html

    def _build_observations(self) -> str:
        """Optional observations article."""
        obs = self.c.st_observations
        if not obs:
            return ""
        return self._art(self._t("special_clauses_title"), f"<p>{_esc(obs)}</p>")

    def _build_signatures(self) -> str:
        t = self._t
        c = self.c
        ep = self.ep
        date_str = _fmt_date(c.date_contrat)
        ville = _esc(c.ville_signature) if c.ville_signature else "Tanger"
        ep_name = _esc(ep.name) if ep else "CASA DI LUSSO SARL"
        st_name = _esc(c.st_name or "Sous-Traitant")

        return f"""
        <div class="st-sig-box">
          <div class="st-sig-info">
            <strong>{t('fait_a')} {ville}</strong>, {t('le')} {date_str},
            {t('en_exemplaires')}
          </div>
          <div class="st-sigs">
            <div class="st-sig">
              <div class="st-sig-label">{t('lbl_ep')}</div>
              <div class="st-sig-note">{t('lu_approuve')}</div>
              <div class="st-sig-line"></div>
              <div class="st-sig-name">{ep_name}</div>
              <div class="st-sig-role">{_esc(ep.qualite_representant) if ep else 'Gérant'}</div>
            </div>
            <div class="st-sig">
              <div class="st-sig-label">{t('lbl_st')}</div>
              <div class="st-sig-note">{t('lu_approuve')}</div>
              <div class="st-sig-line"></div>
              <div class="st-sig-name">{st_name}</div>
              <div class="st-sig-role">{_esc(c.st_qualite or '')}</div>
            </div>
          </div>
          <div class="st-paraphes">{t('paraphes')}</div>
        </div>"""

    def _build_annexe(self) -> str:
        """Annexe – Pièces jointes checklist."""
        t = self._t
        items = st_t("annexe_items", self.lang)
        if not isinstance(items, list):
            return ""

        rows = ""
        for index, item in enumerate(items, start=1):
            rows += f"""
                    <tr>
                        <td class="chk">{index}</td>
                        <td>{_esc(item)}</td>
                        <td class="chk">{_esc(t('annexe_status_blank'))}</td>
                    </tr>"""

        actives = self.c.st_clauses_actives or []
        if "tAnnexe" not in actives:
            return ""

        return f"""
            <div class="st-art">
                <div class="st-art-title">{_esc(t('annexe_title'))}</div>
                <div class="st-art-body">
                    <table class="st-annex-table">
                        <thead>
                            <tr>
                                <th class="chk">{t('annexe_col_no')}</th>
                                <th>{t('annexe_col_doc')}</th>
                                <th class="chk">{t('annexe_col_status')}</th>
                            </tr>
                        </thead>
                        <tbody>{rows}</tbody>
                    </table>
                </div>
            </div>"""

    def _build_footer(self) -> str:
        ep = self.ep
        ep_name = ep.name if ep else "CASA DI LUSSO SARL"
        rc = ep.rc if ep else ""
        now = datetime.now()
        gen_date = now.strftime("%d/%m/%Y")
        gen_time = now.strftime("%H:%M")
        return f"""
        <div class="st-footer">
          <strong>{_esc(ep_name)}</strong> — Entrepreneur Principal<br>
          RC {_esc(rc)} · Tanger, {"Maroc" if self.fr else "Morocco"}<br>
          <em>Document généré le {gen_date} à {gen_time}</em>
        </div>"""

    # ── main assembly ────────────────────────────────────────────────────────

    def _build_html(self) -> str:
        self._art_num = 0  # reset counter
        articles = ""
        articles += self._build_art_parties()
        articles += self._build_art_objet()
        articles += self._build_art_docs()
        articles += self._build_art_prix()
        articles += self._build_art_delais()
        articles += self._build_art_obligations_st()
        articles += self._build_art_obligations_ep()
        articles += self._build_art_assurances()
        articles += self._build_art_reception()
        articles += self._build_art_responsabilite()
        articles += self._build_art_resiliation()
        articles += self._build_art_hse()
        articles += self._build_optional_clauses()
        articles += self._build_trailing_articles()
        articles += self._build_observations()

        return f"""<!DOCTYPE html>
<html lang="{self.lang}">
<head><meta charset="UTF-8"><style>{_ST_CSS}</style></head>
<body>
  <div class="st-topstrip"></div>
  {self._build_header()}
  {self._build_title()}
  {self._build_parties()}
  {articles}
  {self._build_signatures()}
  {self._build_annexe()}
  {self._build_footer()}
</body>
</html>"""

    def generate_response(self) -> HttpResponse:
        """Return an HttpResponse with the generated PDF."""
        html_str = self._build_html()
        pdf_bytes = HTML(string=html_str).write_pdf()
        ref = (self.c.numero_contrat or "contract").replace("/", "-")
        filename = f"contrat_st_{self.c.id}_{ref}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
