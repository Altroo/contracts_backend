from datetime import datetime, timedelta

from django.http import HttpResponse

from weasyprint import HTML

from .pdf import _fmt_date, _fmt_amt, _esc
from .i18n import QUALITE_LABELS
from .bl_i18n import (
    BL_COMPANY,
    FOURNITURES_LABELS,
    EAU_ELEC_LABELS,
    GARANTIE_UNITE_LABELS,
    CLAUSE_RESILIATION_LABELS,
    bl_t,
)


def _garantie_text(contract, lang: str = "fr") -> str:
    """Return e.g. '2 ans' or 'Sans garantie'."""
    nb = int(contract.garantie_nb or 0)
    if nb == 0:
        return bl_t("sans_garantie", lang)
    unite = contract.garantie_unite or "ans"
    labels = GARANTIE_UNITE_LABELS[lang]
    if unite == "mois":
        return f"{nb} {labels['mois']}"
    return f"{nb} {labels['ans_p'] if nb > 1 else labels['ans_s']}"


def _solde_pct(contract) -> float:
    return 100 - float(contract.acompte or 0) - float(contract.tranche2 or 0)


_BL_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600;700&display=swap');

@page {
  size: A4;
  margin: 18mm 18mm 22mm 18mm;
  @bottom-center {
    font-family: 'DM Sans', Arial, sans-serif;
    font-size: 7pt; color: #8a99b3;
    content: "Page " counter(page) " / " counter(pages);
  }
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'DM Sans', Arial, Helvetica, sans-serif;
  font-size: 9pt; color: #1e2d4a; background: #fff; line-height: 1.65;
}

/* ── top strip ── */
.bl-topstrip {
  height: 5px;
  background: linear-gradient(90deg, #0a1628 0%, #2a7fff 50%, #c8a96e 100%);
  margin-bottom: 18pt;
}

/* ── header ── */
.bl-header { display: table; width: 100%; padding-bottom: 14pt; border-bottom: 1pt solid #dce4f0; margin-bottom: 14pt; }
.bl-header-left { display: table-cell; vertical-align: top; }
.bl-header-right { display: table-cell; vertical-align: top; text-align: right; }
.bl-logo { font-family: 'Playfair Display', Georgia, serif; font-size: 20pt; font-weight: 700; color: #0a1628; line-height: 1; }
.bl-logo-tag { font-size: 7pt; color: #c8a96e; letter-spacing: 2px; text-transform: uppercase; margin-top: 3pt; }
.bl-logo-info { font-size: 7pt; color: #8a99b3; line-height: 1.9; margin-top: 5pt; }
.bl-ref { font-family: 'DM Sans', monospace; background: #0a1628; color: #c8a96e; padding: 3pt 9pt; font-size: 9pt; font-weight: 600; letter-spacing: 1px; display: inline-block; margin-bottom: 6pt; border-radius: 3pt; }
.bl-date { font-size: 8pt; color: #8a99b3; line-height: 1.9; }
.bl-date strong { color: #1e2d4a; font-weight: 600; }
.bl-badge { display: inline-block; background: rgba(42,127,255,0.1); color: #2a7fff; padding: 2pt 10pt; font-size: 7.5pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; border-radius: 10pt; margin-top: 4pt; border: 0.5pt solid rgba(42,127,255,0.3); }

/* ── title block ── */
.bl-title { text-align: center; margin: 0 0 16pt; padding: 14pt 0 12pt; border-top: 1pt solid #dce4f0; border-bottom: 1pt solid #dce4f0; position: relative; }
.bl-title::before { content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%); width: 50pt; height: 3pt; background: linear-gradient(90deg, #2a7fff, #c8a96e); border-radius: 0 0 2pt 2pt; }
.bl-title h1 { font-family: 'Playfair Display', Georgia, serif; font-size: 16pt; font-weight: 700; color: #0a1628; margin-bottom: 4pt; }
.bl-subtitle { font-size: 8pt; color: #8a99b3; letter-spacing: 1.5px; }

/* ── parties ── */
.bl-parties { display: table; width: 100%; margin-bottom: 14pt; border-spacing: 10pt 0; }
.bl-party { display: table-cell; width: 50%; padding: 10pt 12pt; vertical-align: top; font-size: 8.5pt; line-height: 1.85; }
.bl-party.prestataire { background: #0a1628; color: rgba(255,255,255,0.85); border-radius: 4pt; }
.bl-party.client { background: rgba(42,127,255,0.04); border: 1pt solid #2a7fff; border-radius: 4pt; }
.bl-party-label { font-size: 7pt; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding-bottom: 5pt; margin-bottom: 6pt; }
.bl-party.prestataire .bl-party-label { color: #c8a96e; border-bottom: 0.5pt solid rgba(200,169,110,0.3); }
.bl-party.client .bl-party-label { color: #2a7fff; border-bottom: 0.5pt solid #2a7fff; }
.bl-party.prestataire strong { color: #fff; }
.bl-party.client strong { color: #0a1628; }

/* ── section titles ── */
.bl-section { font-family: 'Playfair Display', Georgia, serif; font-size: 9pt; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; color: #0a1628; background: rgba(10,22,40,0.04); border-left: 4pt solid #2a7fff; padding: 6pt 10pt 6pt 12pt; margin: 14pt 0 8pt; border-radius: 0 4pt 4pt 0; }

/* ── chantier info grid ── */
.bl-info-grid { display: table; width: 100%; background: #f8fafe; border: 0.5pt solid #dce4f0; border-radius: 6pt; padding: 0; margin-bottom: 6pt; border-spacing: 6pt 0; }
.bl-info-row { display: table-row; }
.bl-info-cell { display: table-cell; padding: 6pt 10pt; width: 33.33%; vertical-align: top; }
.bl-info-label { font-size: 7pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #8a99b3; margin-bottom: 2pt; display: block; }
.bl-info-val { font-size: 8.5pt; font-weight: 600; color: #0a1628; }

/* ── prestations table ── */
.bl-table { width: 100%; border-collapse: collapse; font-size: 8.5pt; margin: 7pt 0; }
.bl-table thead tr { background: #0a1628; }
.bl-table th { color: #fff; padding: 6pt 9pt; text-align: left; font-size: 7pt; letter-spacing: 0.5px; font-weight: 600; }
.bl-table th:last-child { text-align: right; }
.bl-table td { padding: 6pt 9pt; border-bottom: 0.5pt solid #dce4f0; vertical-align: top; }
.bl-table td:last-child { text-align: right; font-weight: 600; color: #0a1628; }
.bl-table tr:nth-child(even) td { background: rgba(240,244,250,0.4); }
.bl-desc-small { font-size: 7pt; color: #8a99b3; margin-top: 2pt; }

/* ── totals ── */
.bl-totaux { text-align: right; margin-top: 8pt; }
.bl-totaux-box { display: inline-block; min-width: 220pt; text-align: left; }
.bl-total-row { display: table; width: 100%; padding: 4pt 0; font-size: 8.5pt; border-bottom: 0.5pt solid #dce4f0; }
.bl-total-row .lbl { display: table-cell; }
.bl-total-row .val { display: table-cell; text-align: right; font-weight: 600; }
.bl-total-row.grand { border-bottom: none; border-top: 2pt solid #0a1628; margin-top: 4pt; padding-top: 8pt; font-size: 11pt; font-weight: 700; color: #0a1628; }
.bl-total-row.grand .val { color: #2a7fff; }

/* ── payment schedule ── */
.bl-ech-grid { display: table; width: 100%; margin: 8pt 0; border-spacing: 6pt 0; }
.bl-ech { display: table-cell; padding: 10pt; border: 1pt solid #dce4f0; border-radius: 6pt; vertical-align: top; }
.bl-ech.acompte  { border-color: rgba(200,169,110,0.5); background: rgba(200,169,110,0.06); }
.bl-ech.tranche2 { border-color: rgba(42,127,255,0.3); background: rgba(42,127,255,0.04); }
.bl-ech.solde    { border-color: rgba(34,197,94,0.4); background: rgba(34,197,94,0.04); }
.bl-ech-label { font-size: 7pt; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #8a99b3; margin-bottom: 4pt; }
.bl-ech-amount { font-size: 14pt; font-weight: 700; color: #0a1628; }
.bl-ech-detail { font-size: 7pt; color: #8a99b3; margin-top: 3pt; }

/* ── articles ── */
.bl-art { margin-bottom: 10pt; page-break-inside: avoid; }
.bl-art-title { font-size: 8pt; font-weight: 700; color: #0a1628; background: rgba(10,22,40,0.04); padding: 5pt 10pt; border: 0.5pt solid #dce4f0; border-bottom: 1pt solid #dce4f0; border-radius: 4pt 4pt 0 0; }
.bl-art-body { font-size: 8.5pt; color: #3a4e6e; padding: 8pt 10pt; line-height: 1.75; border: 0.5pt solid #dce4f0; border-top: none; border-radius: 0 0 4pt 4pt; }
.bl-art-body p { margin-bottom: 4pt; }
.bl-art-body strong { color: #0a1628; }
.bl-garantie-badge { display: inline-block; background: rgba(34,197,94,0.1); color: #16a34a; padding: 1pt 8pt; border-radius: 10pt; font-weight: 700; font-size: 8pt; border: 0.5pt solid rgba(34,197,94,0.3); }
.bl-no-garantie-badge { display: inline-block; background: rgba(239,68,68,0.08); color: #dc2626; padding: 1pt 8pt; border-radius: 10pt; font-weight: 700; font-size: 8pt; border: 0.5pt solid rgba(239,68,68,0.2); }

/* ── signatures ── */
.bl-sig-box { margin-top: 18pt; border-top: 1.5pt solid #dce4f0; padding-top: 14pt; page-break-inside: avoid; }
.bl-sig-info { font-size: 8.5pt; padding: 8pt 12pt; background: rgba(42,127,255,0.04); border: 0.5pt solid rgba(42,127,255,0.15); border-radius: 4pt; margin-bottom: 12pt; }
.bl-sigs { display: table; width: 100%; border-spacing: 12pt 0; }
.bl-sig { display: table-cell; width: 50%; border: 1pt solid #dce4f0; padding: 10pt; vertical-align: top; border-radius: 4pt; }
.bl-sig-label { font-size: 7pt; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; color: #2a7fff; margin-bottom: 3pt; }
.bl-sig-note { font-size: 8pt; color: #8a99b3; margin-bottom: 6pt; font-style: italic; }
.bl-sig-line { border-bottom: 0.5pt dashed #ccc; height: 40pt; margin-bottom: 6pt; }
.bl-sig-name { font-size: 8.5pt; font-weight: 600; color: #0a1628; }
.bl-sig-role { font-size: 7.5pt; color: #8a99b3; }

/* ── footer ── */
.bl-footer { margin-top: 12pt; padding-top: 7pt; border-top: 0.5pt solid #dce4f0; text-align: center; font-size: 7pt; color: #8a99b3; line-height: 1.9; }
.bl-footer strong { color: #0a1628; }
"""


class BluelinePDFGenerator:
    """Generate a WeasyPrint PDF for a Blueline Works contract."""

    def __init__(self, contract, language: str = "fr"):
        self.c = contract
        self.lang = language
        self.fr = language == "fr"

    def _t(self, key: str) -> str:
        return bl_t(key, self.lang)

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

    @property
    def _acompte_pct(self) -> float:
        return float(self.c.acompte if self.c.acompte is not None else 30)

    @property
    def _tranche2_pct(self) -> float:
        return float(self.c.tranche2 or 0)

    @property
    def _solde_pct(self) -> float:
        return _solde_pct(self.c)

    def _dev(self) -> str:
        return self.c.devise or "MAD"

    def _amt(self, n) -> str:
        return _fmt_amt(n, self._dev())

    def _date_fin(self) -> str:
        if self.c.date_debut and self.c.duree_estimee:
            try:
                d = self.c.date_debut + timedelta(days=int(self.c.duree_estimee))
                return _fmt_date(d)
            except (TypeError, ValueError):
                pass
        return "—"

    def _build_header(self) -> str:
        co = BL_COMPANY
        tagline = co["tagline_fr"] if self.fr else co["tagline_en"]
        return f"""
        <div class="bl-header">
          <div class="bl-header-left">
            <div class="bl-logo">{_esc(co['name'])}</div>
            <div class="bl-logo-tag">{_esc(tagline)}</div>
            <div class="bl-logo-info">
              📞&nbsp;{_esc(co['phone'])}&nbsp;&nbsp;✉&nbsp;{_esc(co['email'])}<br>
              📍&nbsp;{_esc(co['address'])}<br>
              🏛&nbsp;{self._t('ice')} : {_esc(co['ice'])}
            </div>
          </div>
          <div class="bl-header-right">
            <div class="bl-ref">N° {_esc(self.c.numero_contrat or '')}</div><br>
            <div class="bl-date">{self._t('date_sig')} : <strong>{_fmt_date(self.c.date_contrat)}</strong></div>
            <div><span class="bl-badge">{self._t('badge')}</span></div>
          </div>
        </div>"""

    def _build_title(self) -> str:
        return f"""
        <div class="bl-title">
          <h1>{self._t('contrat_title')}</h1>
          <div class="bl-subtitle">{self._t('contrat_subtitle')}</div>
        </div>"""

    def _build_parties(self) -> str:
        co = BL_COMPANY
        c = self.c
        return f"""
        <div class="bl-section">{self._t('parties_title')}</div>
        <div class="bl-parties">
          <div class="bl-party prestataire">
            <div class="bl-party-label">{self._t('prestataire_label')}</div>
            <strong>{_esc(co['name'])}</strong><br>
            {_esc(self._t('prestataire_desc')).replace(chr(10), '<br>')}<br>
            <strong>{self._t('tel')} :</strong> {_esc(co['phone'])}<br>
            <strong>{self._t('email')} :</strong> {_esc(co['email'])}<br>
            <strong>{self._t('ice')} :</strong> {_esc(co['ice'])}<br>
            <strong>{self._t('adresse')} :</strong> {_esc(co['address'])}
          </div>
          <div class="bl-party client">
            <div class="bl-party-label">{self._t('client_label')}</div>
            {"<strong>" + _esc(c.client_nom) + "</strong><br>" if c.client_nom else ""}
            {"<strong>" + self._t('adresse') + " :</strong> " + _esc(c.client_adresse or '') + (" — " + _esc(c.client_ville or '') if c.client_ville else '') + (" " + _esc(c.client_cp or '') if c.client_cp else '') + "<br>" if c.client_adresse else ''}
            {"<strong>" + self._t('tel') + " :</strong> " + _esc(c.client_tel or '') + "<br>" if c.client_tel else ''}
            {"<strong>" + self._t('email') + " :</strong> " + _esc(c.client_email or '') + "<br>" if c.client_email else ''}
            {"<strong>" + self._t('cin_ice') + " :</strong> " + _esc(c.client_cin or '') + "<br>" if c.client_cin else ''}
            <strong>{self._t('qualite')} :</strong> {_esc(QUALITE_LABELS[self.lang].get(c.client_qualite or '', c.client_qualite or ('Personne Physique' if self.fr else 'Individual')))}
          </div>
        </div>"""

    def _build_chantier(self) -> str:
        c = self.c
        etage_str = f" — {_esc(c.chantier_etage)}" if c.chantier_etage else ""
        surface = f"{c.surface} m²" if c.surface else ""
        duree_str = ""
        if c.duree_estimee:
            duree_str = f" ({_esc(c.duree_estimee)} {self._t('jours_ouvrables')})"
        date_fin_val = self._date_fin()

        _EMPTY = {"—", "…… / …… / ………", ""}

        def _cell(label, value):
            if not value or value in _EMPTY:
                return ""
            return (
                f'<div class="bl-info-cell">'
                f'<span class="bl-info-label">{label}</span>'
                f'<span class="bl-info-val">{value}</span>'
                f"</div>"
            )

        adresse_val = (_esc(c.adresse_travaux) + etage_str) if c.adresse_travaux else ""
        fin_val = (date_fin_val + duree_str) if date_fin_val not in _EMPTY else ""

        active_cells = list(
            filter(
                None,
                [
                    _cell(self._t("adresse_chantier"), adresse_val),
                    _cell(
                        self._t("ville"),
                        _esc(c.chantier_ville) if c.chantier_ville else "",
                    ),
                    _cell(
                        self._t("type_bien"),
                        _esc(c.get_type_bien_display()) if c.type_bien else "",
                    ),
                    _cell(self._t("surface_totale"), _esc(surface) if surface else ""),
                    _cell(
                        self._t("date_debut"),
                        _fmt_date(c.date_debut) if c.date_debut else "",
                    ),
                    _cell(self._t("fin_estimee"), fin_val),
                ],
            )
        )

        rows_html = ""
        for i in range(0, len(active_cells), 3):
            row = "".join(active_cells[i : i + 3])
            rows_html += f'<div class="bl-info-row">{row}</div>\n          '

        desc_html = ""
        if c.description_travaux:
            desc_html = (
                f'<div style="margin-top:6pt;padding:6pt 10pt;background:rgba(42,127,255,0.04);'
                f"border:0.5pt solid rgba(42,127,255,0.15);border-radius:4pt;font-size:8.5pt;"
                f'line-height:1.75;color:#3a4e6e;">'
                f'<strong style="color:#0a1628">{self._t("description_travaux_label")}</strong><br>'
                + _esc(c.description_travaux).replace("\n", "<br>")
                + "</div>"
            )

        return f"""
        <div class="bl-section">{self._t('chantier_title')}</div>
        <div class="bl-info-grid">
          {rows_html}
        </div>
        {desc_html}"""

    def _build_prestations(self) -> str:
        c = self.c
        prestations = c.prestations or []
        if not prestations:
            no_prest = self._t("aucune_prestation")
            rows = f'<tr><td colspan="5" style="text-align:center;color:#8a99b3;padding:14pt">{no_prest}</td></tr>'
        else:
            rows = ""
            for i, p in enumerate(prestations, 1):
                nom = _esc(p.get("nom", ""))
                desc = _esc(p.get("description", p.get("desc", "")))
                qte = p.get("quantite", p.get("qte", 0))
                unite = _esc(p.get("unite", ""))
                pu = float(p.get("prix_unitaire", p.get("pu", 0)))
                total = float(qte) * pu
                desc_html = f'<div class="bl-desc-small">{desc}</div>' if desc else ""
                rows += f"""
                <tr>
                  <td><strong>{i}. {nom}</strong>{desc_html}</td>
                  <td>{qte} {unite}</td>
                  <td>{self._amt(pu)}</td>
                  <td>{int(self._tva_pct)}%</td>
                  <td>{self._amt(total)}</td>
                </tr>"""

        return f"""
        <div class="bl-section">{self._t('prestations_title')}</div>
        <table class="bl-table">
          <thead>
            <tr>
              <th style="width:40%">{self._t('th_designation')}</th>
              <th>{self._t('th_qty')}</th>
              <th>{self._t('th_pu')}</th>
              <th>{self._t('th_tva')}</th>
              <th>{self._t('th_montant')}</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
        <div class="bl-totaux"><div class="bl-totaux-box">
          <div class="bl-total-row"><span class="lbl">{self._t('subtotal_ht')}</span><span class="val">{self._amt(self._ht)}</span></div>
          <div class="bl-total-row"><span class="lbl">{'TVA' if self.fr else 'VAT'} ({self._tva_pct:g}%)</span><span class="val">{self._amt(self._tva_amt)}</span></div>
          <div class="bl-total-row grand"><span class="lbl">{self._t('total_ttc')}</span><span class="val">{self._amt(self._ttc)}</span></div>
        </div></div>"""

    def _build_payment(self) -> str:
        ttc = self._ttc
        ap, t2p, sp = self._acompte_pct, self._tranche2_pct, self._solde_pct
        mont_a = ttc * ap / 100
        mont_t2 = ttc * t2p / 100
        mont_s = ttc * sp / 100

        t2_block = ""
        if t2p > 0:
            t2_block = f"""
            <div class="bl-ech tranche2">
              <div class="bl-ech-label">{self._t('tranche2_label')} ({t2p:.0f}%)</div>
              <div class="bl-ech-amount">{self._amt(mont_t2)}</div>
              <div class="bl-ech-detail">{self._t('tranche2_detail')}</div>
            </div>"""

        mode = _esc(self.c.mode_paiement_texte or "")
        rib_html = ""
        if self.c.rib:
            rib_html = f"<br><strong>{self._t('coord_bancaires')} :</strong> {_esc(self.c.rib)}"

        return f"""
        <div class="bl-section">{self._t('paiement_title')}</div>
        <div class="bl-ech-grid">
          <div class="bl-ech acompte">
            <div class="bl-ech-label">{self._t('acompte_label')} ({ap:.0f}%)</div>
            <div class="bl-ech-amount">{self._amt(mont_a)}</div>
            <div class="bl-ech-detail">{self._t('acompte_detail')}</div>
          </div>
          {t2_block}
          <div class="bl-ech solde">
            <div class="bl-ech-label">{self._t('solde_label')} ({sp:.0f}%)</div>
            <div class="bl-ech-amount">{self._amt(mont_s)}</div>
            <div class="bl-ech-detail">{self._t('solde_detail')}</div>
          </div>
        </div>
        <p style="font-size:8.5pt;margin-top:6pt;">
          <strong>{self._t('mode_paiement')} :</strong> {mode}{rib_html}
        </p>"""

    def _art(self, title_key: str, body: str) -> str:
        return f"""
        <div class="bl-art">
          <div class="bl-art-title">{self._t(title_key)}</div>
          <div class="bl-art-body">{body}</div>
        </div>"""

    def _build_articles(self) -> str:
        c = self.c
        lang = self.lang
        client = _esc(c.client_nom or "le Client")
        co_name = BL_COMPANY["name"]

        # Garantie
        g_nb = int(c.garantie_nb or 0)
        g_text = _garantie_text(c, lang)
        g_badge = (
            f'<span class="bl-no-garantie-badge">{g_text}</span>'
            if g_nb == 0
            else f'<span class="bl-garantie-badge">{g_text}</span>'
        )
        # Fournitures
        fournitures_val = c.fournitures or "non_incluses"
        fournitures_text = FOURNITURES_LABELS.get(lang, FOURNITURES_LABELS["fr"]).get(
            fournitures_val, FOURNITURES_LABELS["fr"]["non_incluses"]
        )

        # Eau & elec
        eau_val = c.eau_electricite or "client"
        eau_text = EAU_ELEC_LABELS.get(lang, EAU_ELEC_LABELS["fr"]).get(
            eau_val, EAU_ELEC_LABELS["fr"]["client"]
        )

        # Materiaux
        mat_html = ""
        if c.materiaux_detail:
            mat_label = (
                "Matériaux à fournir par le client"
                if self.fr
                else "Materials to be supplied by the client"
            )
            mat_html = f"<br><strong>{mat_label} :</strong> {_esc(c.materiaux_detail)}."

        # Dates
        date_debut_str = _fmt_date(c.date_debut)
        date_fin_str = self._date_fin()
        duree_str = ""
        if c.duree_estimee:
            duree_str = (
                f" (durée estimée : <strong>{_esc(c.duree_estimee)} {self._t('jours_ouvrables')}</strong>)"
                if self.fr
                else f" (estimated duration: <strong>{_esc(c.duree_estimee)} {self._t('jours_ouvrables')}</strong>)"
            )

        # Solde
        sp = self._solde_pct
        mont_solde = self._ttc * sp / 100

        # Pénalités
        if c.penalite_retard:
            _pv = f"{c.penalite_retard:g}"
            if self.fr:
                _pv = _pv.replace(".", ",")
            penalites = _esc(f"{_pv}% par mois" if self.fr else f"{_pv}% per month")
        else:
            penalites = "1,5% par mois" if self.fr else "1.5% per month"

        # Résiliation
        resil_val = c.clause_resiliation or "30j"
        resil_text = CLAUSE_RESILIATION_LABELS.get(
            lang, CLAUSE_RESILIATION_LABELS["fr"]
        ).get(resil_val, CLAUSE_RESILIATION_LABELS["fr"]["30j"])

        # Tribunal
        tribunal = _esc(c.tribunal or "Tribunal de Commerce de Casablanca")

        # Exclusions garantie
        excl_garantie = _esc(
            c.exclusions_garantie
            or (
                "Usure normale, mauvaise utilisation, modifications par des tiers."
                if self.fr
                else "Normal wear, misuse, modifications by third parties."
            )
        )

        articles_html = (
            '<div class="bl-section">' + self._t("articles_title") + "</div>"
        )

        # Art 1 — Objet
        if self.fr:
            art1 = (
                f"Le présent contrat a pour objet la réalisation par <strong>{co_name}</strong> "
                f'(ci-après le "Prestataire") des travaux de pose de carrelage, marbre, finitions '
                f"et travaux connexes décrits dans le tableau des prestations, au bénéfice de "
                f'<strong>{client}</strong> (ci-après le "Client"), sur le chantier situé à '
                f"l'adresse indiquée. Le Prestataire s'engage à exécuter ces travaux dans les "
                f"règles de l'art, avec tout le soin et le professionnalisme requis."
            )
        else:
            art1 = (
                f"The purpose of this contract is the execution by <strong>{co_name}</strong> "
                f'(hereinafter "The Service Provider") of tiling, marble, finishing and related '
                f"works described in the services table, for the benefit of "
                f'<strong>{client}</strong> (hereinafter "The Client"), at the site located '
                f"at the specified address. The Service Provider undertakes to execute these works "
                f"in compliance with professional standards, with all due care and professionalism."
            )
        articles_html += self._art("art1_title", art1)

        # Art 2 — Fournitures & Matériaux
        if self.fr:
            art2 = (
                f"<strong>Fournitures :</strong> {fournitures_text}."
                f"{mat_html}<br>"
                f"<strong>Eau & Électricité :</strong> {eau_text}<br>"
                f"Les matériaux fournis par le Client doivent être disponibles sur chantier au "
                f"minimum <strong>24 heures avant</strong> le début des travaux concernés. Tout "
                f"retard de livraison des matériaux imputable au Client pourra entraîner un "
                f"décalage du planning et/ou une facturation complémentaire."
            )
        else:
            art2 = (
                f"<strong>Supplies:</strong> {fournitures_text}."
                f"{mat_html}<br>"
                f"<strong>Water & Electricity:</strong> {eau_text}<br>"
                f"Materials supplied by the Client must be available on site at least "
                f"<strong>24 hours before</strong> the start of the relevant works. Any delay "
                f"in material delivery attributable to the Client may result in schedule "
                f"adjustments and/or additional charges."
            )
        articles_html += self._art("art2_title", art2)

        # Art 3 — Délais
        if self.fr:
            art3 = (
                f"Les travaux débuteront le <strong>{date_debut_str}</strong> et se termineront "
                f"le <strong>{date_fin_str}</strong>{duree_str}. Ces délais sont donnés de bonne "
                f"foi à titre indicatif et peuvent être prolongés en cas de : (i) force majeure, "
                f"(ii) retard de livraison des matériaux non imputable au Prestataire, (iii) "
                f"mauvaises conditions climatiques, (iv) modifications demandées par le Client "
                f"en cours de chantier, ou (v) arrêt de chantier causé par le Client. Tout arrêt "
                f"injustifié imputé au Client fera l'objet d'une facturation complémentaire "
                f"couvrant les frais de mobilisation et d'immobilisation des équipes."
            )
        else:
            art3 = (
                f"Works will begin on <strong>{date_debut_str}</strong> and end on "
                f"<strong>{date_fin_str}</strong>{duree_str}. These deadlines are given in good "
                f"faith as estimates and may be extended in the event of: (i) force majeure, "
                f"(ii) material delivery delays not attributable to the Service Provider, (iii) "
                f"adverse weather conditions, (iv) modifications requested by the Client during "
                f"works, or (v) site shutdown caused by the Client. Any unjustified shutdown "
                f"attributable to the Client will be subject to additional charges covering "
                f"mobilization and immobilization costs."
            )
        articles_html += self._art("art3_title", art3)

        # Art 4 — Garantie
        if self.fr:
            if g_nb == 0:
                art4 = (
                    f"Les travaux objets du présent contrat sont réalisés {g_badge}. Le Client "
                    f"reconnaît avoir été expressément informé de cette absence de garantie "
                    f"contractuelle et l'accepte. Cette disposition ne remet pas en cause les "
                    f"obligations légales du Prestataire telles que définies par la législation "
                    f"marocaine en vigueur."
                )
            else:
                art4 = (
                    f"Les travaux sont couverts par une garantie {g_badge} "
                    f"à compter de la date de réception et de signature du procès-verbal de réception, contre tout "
                    f"défaut d'exécution directement imputable au Prestataire."
                )
            art4 += f"<br><br><strong>Exclusions de garantie :</strong> {excl_garantie}"
        else:
            if g_nb == 0:
                art4 = (
                    f"The works subject to this contract are performed {g_badge}. The Client "
                    f"acknowledges having been expressly informed of this absence of contractual "
                    f"guarantee and accepts it. This provision does not affect the Service "
                    f"Provider's legal obligations as defined by current Moroccan legislation."
                )
            else:
                art4 = (
                    f"The works are covered by a {g_badge} guarantee "
                    f"from the date of reception and signing of the acceptance report, against any execution defect directly "
                    f"attributable to the Service Provider."
                )
            art4 += f"<br><br><strong>Warranty exclusions:</strong> {excl_garantie}"
        articles_html += self._art("art4_title", art4)

        # Art 5 — Réception
        if self.fr:
            art5 = (
                f"La réception des travaux est effectuée contradictoirement à l'issue des "
                f"travaux. Un <strong>procès-verbal de réception</strong> sera établi et signé "
                f"par les deux parties. Le solde du contrat (<strong>{sp:.0f}%</strong> soit "
                f"<strong>{self._amt(mont_solde)}</strong>) est exigible immédiatement à la "
                f"signature de ce procès-verbal. Toute réserve devra être notifiée par écrit "
                f"dans les <strong>48 heures</strong> suivant la fin des travaux ; l'absence "
                f"de réserve dans ce délai vaut acceptation définitive. Les travaux réservés "
                f"feront l'objet d'une reprise dans un délai convenu entre les parties."
            )
        else:
            art5 = (
                f"Works reception is carried out jointly at the completion of works. An "
                f"<strong>acceptance report</strong> will be drawn up and signed by both parties. "
                f"The contract balance (<strong>{sp:.0f}%</strong>, i.e. "
                f"<strong>{self._amt(mont_solde)}</strong>) is payable immediately upon signing "
                f"this report. Any reservations must be notified in writing within "
                f"<strong>48 hours</strong> of the end of works; absence of reservations within "
                f"this period constitutes final acceptance. Reserved works will be subject to "
                f"rework within a timeframe agreed between the parties."
            )
        articles_html += self._art("art5_title", art5)

        # Art 6 — Retards de paiement
        if self.fr:
            art6 = (
                f"Tout retard de paiement entraînera l'application de pénalités de retard au "
                f"taux de <strong>{penalites}</strong>, calculées à partir du lendemain de la "
                f"date d'échéance, sans qu'une mise en demeure préalable soit nécessaire. Le "
                f"Prestataire se réserve le droit de <strong>suspendre les travaux</strong> en "
                f"cas de non-paiement après mise en demeure restée sans effet pendant 72 heures. "
                f"Les frais de recouvrement éventuels seront à la charge du Client."
            )
        else:
            art6 = (
                f"Any late payment will result in the application of late payment penalties "
                f"at the rate of <strong>{penalites}</strong>, calculated from the day after "
                f"the due date, without prior notice being necessary. The Service Provider "
                f"reserves the right to <strong>suspend works</strong> in case of non-payment "
                f"after a formal notice that remains unanswered for 72 hours. Any recovery "
                f"costs will be borne by the Client."
            )
        articles_html += self._art("art6_title", art6)

        # Art 7 — Résiliation
        if self.fr:
            art7 = (
                f"{resil_text} En cas de résiliation anticipée à l'initiative du Client, les "
                f"travaux déjà réalisés seront facturés au prorata de leur avancement constaté "
                f"contradictoirement, et l'acompte versé restera acquis au Prestataire à titre "
                f"d'indemnité forfaitaire de dédit couvrant les préjudices subis (mobilisation "
                f"du matériel, main-d'œuvre réservée, sous-traitants engagés, etc.)."
            )
        else:
            resil_en = CLAUSE_RESILIATION_LABELS.get("en", {}).get(resil_val, "")
            art7 = (
                f"{resil_en} In case of early termination at the Client's initiative, the "
                f"works already completed will be invoiced pro rata based on jointly verified "
                f"progress, and the deposit paid will remain retained by the Service Provider "
                f"as a fixed penalty covering damages suffered (equipment mobilization, "
                f"reserved workforce, engaged subcontractors, etc.)."
            )
        articles_html += self._art("art7_title", art7)

        # Art 8 — Sécurité
        if self.fr:
            art8 = (
                "Le Prestataire s'engage à : (i) respecter les règles de sécurité en vigueur, "
                "(ii) maintenir le chantier dans un état de propreté acceptable, (iii) protéger "
                "les zones adjacentes non concernées par les travaux. Le Client s'engage à : "
                "(i) faciliter l'accès au chantier aux horaires convenus (généralement 8h00–18h00, "
                "du lundi au samedi), (ii) évacuer les meubles et objets gênants avant le début "
                "des travaux, (iii) informer le Prestataire de toute contrainte particulière "
                "(copropriété, voisinage, etc.)."
            )
        else:
            art8 = (
                "The Service Provider undertakes to: (i) respect safety regulations in force, "
                "(ii) maintain the site in an acceptable state of cleanliness, (iii) protect "
                "adjacent areas unaffected by the works. The Client undertakes to: (i) facilitate "
                "access to the site during agreed hours (generally 8:00 AM - 6:00 PM, Monday "
                "to Saturday), (ii) remove furniture and obstructing items before works begin, "
                "(iii) inform the Service Provider of any particular constraints (condominium, "
                "neighbors, etc.)."
            )
        articles_html += self._art("art8_title", art8)

        # Art 9 — Responsabilité
        if self.fr:
            art9 = (
                "Le Prestataire déclare être couvert par une assurance responsabilité civile "
                "professionnelle couvrant les travaux objets du présent contrat. Sa responsabilité "
                "ne peut être engagée pour : les dommages résultant d'une mauvaise utilisation "
                "des ouvrages réalisés, des modifications effectuées par des tiers non mandatés, "
                "des vices cachés dans les matériaux fournis par le Client, ou des sinistres "
                "survenus après l'expiration de la garantie contractuelle."
            )
        else:
            art9 = (
                "The Service Provider declares to be covered by professional liability insurance "
                "covering the works subject to this contract. Their liability cannot be engaged "
                "for: damages resulting from misuse of completed works, modifications made by "
                "unauthorized third parties, hidden defects in materials supplied by the Client, "
                "or incidents occurring after the expiration of the contractual guarantee."
            )
        articles_html += self._art("art9_title", art9)

        # Art 10 — Données personnelles
        if self.fr:
            art10 = (
                f"Les données personnelles collectées dans le cadre de ce contrat (nom, adresse, "
                f"coordonnées) sont utilisées exclusivement pour la gestion de la relation "
                f"contractuelle entre {co_name} et le Client. Elles ne seront en aucun cas "
                f"cédées à des tiers. Le Client dispose d'un droit d'accès, de rectification "
                f"et de suppression de ses données conformément à la législation en vigueur."
            )
        else:
            art10 = (
                f"Personal data collected under this contract (name, address, contact details) "
                f"is used exclusively for managing the contractual relationship between "
                f"{co_name} and the Client. It will under no circumstances be transferred to "
                f"third parties. The Client has the right to access, rectify and delete their "
                f"data in compliance with current legislation."
            )
        articles_html += self._art("art10_title", art10)

        # Art 11 — Litiges
        if self.fr:
            art11 = (
                f"En cas de différend relatif à l'exécution ou à l'interprétation du présent "
                f"contrat, les parties s'engagent à rechercher une <strong>solution amiable</strong> "
                f"dans un délai de 30 jours à compter de la notification du différend. À défaut "
                f"d'accord amiable, le litige sera porté exclusivement devant le "
                f"<strong>{tribunal}</strong>, nonobstant pluralité de défendeurs ou appel en "
                f"garantie, même pour les procédures d'urgence ou conservatoires."
            )
        else:
            art11 = (
                f"In the event of a dispute relating to the execution or interpretation of this "
                f"contract, the parties undertake to seek an <strong>amicable solution</strong> "
                f"within 30 days of notification of the dispute. Failing amicable agreement, the "
                f"dispute will be brought exclusively before the <strong>{tribunal}</strong>, "
                f"notwithstanding plurality of defendants or warranty appeals, including for "
                f"emergency or conservatory proceedings."
            )
        articles_html += self._art("art11_title", art11)

        # Notes
        if c.notes:
            articles_html += self._art("notes_title", _esc(c.notes))

        return articles_html

    def _build_signatures(self) -> str:
        c = self.c
        date_str = _fmt_date(c.date_contrat)
        ville = _esc(c.ville_signature) if c.ville_signature else "Tanger"
        return f"""
        <div class="bl-sig-box">
          <div class="bl-sig-info">
            <strong>{self._t('fait_a')} {ville}</strong>, {self._t('le')} {date_str},
            {self._t('en_deux_ex')}
          </div>
          <div class="bl-sigs">
            <div class="bl-sig">
              <div class="bl-sig-label">{self._t('prestataire_label')}</div>
              <div class="bl-sig-note">{self._t('sig_cachet')}</div>
              <div class="bl-sig-line"></div>
              <div class="bl-sig-name">{BL_COMPANY['name']}</div>
              <div class="bl-sig-role">{self._t('date_sig')} : _______________</div>
            </div>
            <div class="bl-sig">
              <div class="bl-sig-label">{self._t('client_label')}</div>
              <div class="bl-sig-note">{self._t('lu_approuve')}</div>
              <div class="bl-sig-line"></div>
              <div class="bl-sig-name">{_esc(c.client_nom or 'Client')}</div>
              <div class="bl-sig-role">{self._t('date_sig')} : _______________</div>
            </div>
          </div>
        </div>"""

    def _build_footer(self) -> str:
        co = BL_COMPANY
        now = datetime.now()
        gen_date = now.strftime("%d/%m/%Y")
        gen_time = now.strftime("%H:%M")
        return f"""
        <div class="bl-footer">
          <strong>{co['name']}</strong> — {self._t('footer_specialist')}<br>
          {_esc(co['phone'])} | {_esc(co['email'])} | {self._t('ice')} : {co['ice']}<br>
          <em>{self._t('doc_genere')} {gen_date} {self._t('a')} {gen_time} — {self._t('valeur_juridique')}</em>
        </div>"""

    def _build_html(self) -> str:
        return f"""<!DOCTYPE html>
<html lang="{self.lang}">
<head><meta charset="UTF-8"><style>{_BL_CSS}</style></head>
<body>
  <div class="bl-topstrip"></div>
  {self._build_header()}
  {self._build_title()}
  {self._build_parties()}
  {self._build_chantier()}
  {self._build_prestations()}
  {self._build_payment()}
  {self._build_articles()}
  {self._build_signatures()}
  {self._build_footer()}
</body>
</html>"""

    def generate_response(self) -> HttpResponse:
        """Return an HttpResponse with the generated PDF."""
        html_str = self._build_html()
        pdf_bytes = HTML(string=html_str).write_pdf()
        ref = (self.c.numero_contrat or "contract").replace("/", "-")
        filename = f"contrat_{self.c.id}_{ref}.pdf"
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
