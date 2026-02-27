from io import BytesIO

from django.http import HttpResponse
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, RGBColor, Cm
from docx.enum.table import WD_TABLE_ALIGNMENT

BRAND_COLOR = RGBColor(0x1A, 0x2E, 0x4A)
ACCENT_COLOR = RGBColor(0xC9, 0xA8, 0x4C)
LIGHT_GRAY = RGBColor(0xF5, 0xF5, 0xF5)

DOC_LABELS = {
    "fr": {
        "title": "CONTRAT DE PRESTATIONS",
        "ref": "Référence",
        "date": "Date",
        "statut": "Statut",
        "section_client": "INFORMATIONS CLIENT",
        "nom": "Nom & Prénom",
        "cin": "CIN / ICE / Passeport",
        "qualite": "Qualité",
        "adresse": "Adresse",
        "tel": "Téléphone",
        "email": "Email",
        "ville_sig": "Ville de Signature",
        "section_project": "PROJET & SERVICES",
        "adresse_tx": "Adresse des Travaux",
        "type_bien": "Type de Bien",
        "surface": "Surface (m²)",
        "services": "Services",
        "description": "Description",
        "date_debut": "Date de Début",
        "duree": "Durée Estimée",
        "acces": "Conditions d'Accès",
        "section_financial": "CONDITIONS FINANCIÈRES",
        "montant_ht": "Montant HT",
        "tva": "TVA",
        "montant_ttc": "Montant TTC",
        "tranches": "Échéancier",
        "mode_paiement": "Mode de Paiement",
        "rib": "RIB / Coordonnées Bancaires",
        "delai_retard": "Délai Retard Toléré",
        "penalite": "Pénalité Retard",
        "frais_redemarrage": "Frais de Redémarrage",
        "section_clauses": "CLAUSES JURIDIQUES",
        "garantie": "Durée de Garantie",
        "delai_reserves": "Délai Réserves",
        "tribunal": "Tribunal Compétent",
        "clauses": "Clauses Actives",
        "clause_spec": "Clauses Spécifiques",
        "exclusions": "Exclusions",
        "section_options": "OPTIONS & PRÉSENTATION",
        "type_contrat": "Type de Contrat",
        "responsable": "Responsable Projet",
        "architecte": "Architecte / Designer",
        "confidentialite": "Confidentialité",
        "version": "Version",
        "annexes": "Annexes",
        "section_signatures": "SIGNATURES",
        "signature_client": "Signature du Client",
        "signature_cdl": "Signature CASA DI LUSSO",
        "lu_approuve": "Lu et Approuvé",
        "days": "jours",
        "per_day": "%/j",
        "not_specified": "Non spécifié",
    },
    "en": {
        "title": "SERVICE CONTRACT",
        "ref": "Reference",
        "date": "Date",
        "statut": "Status",
        "section_client": "CLIENT INFORMATION",
        "nom": "Full Name",
        "cin": "ID / Passport",
        "qualite": "Capacity",
        "adresse": "Address",
        "tel": "Phone",
        "email": "Email",
        "ville_sig": "Signing City",
        "section_project": "PROJECT & SERVICES",
        "adresse_tx": "Work Address",
        "type_bien": "Property Type",
        "surface": "Area (m²)",
        "services": "Services",
        "description": "Description",
        "date_debut": "Start Date",
        "duree": "Estimated Duration",
        "acces": "Access Conditions",
        "section_financial": "FINANCIAL TERMS",
        "montant_ht": "Amount (excl. VAT)",
        "tva": "VAT",
        "montant_ttc": "Total (incl. VAT)",
        "tranches": "Payment Schedule",
        "mode_paiement": "Payment Method",
        "rib": "Bank Details",
        "delai_retard": "Grace Period",
        "penalite": "Late Penalty",
        "frais_redemarrage": "Restart Fee",
        "section_clauses": "LEGAL CLAUSES",
        "garantie": "Warranty Period",
        "delai_reserves": "Snagging Period",
        "tribunal": "Jurisdiction",
        "clauses": "Active Clauses",
        "clause_spec": "Specific Clauses",
        "exclusions": "Exclusions",
        "section_options": "OPTIONS & PRESENTATION",
        "type_contrat": "Contract Type",
        "responsable": "Project Manager",
        "architecte": "Architect / Designer",
        "confidentialite": "Confidentiality",
        "version": "Version",
        "annexes": "Annexes",
        "section_signatures": "SIGNATURES",
        "signature_client": "Client Signature",
        "signature_cdl": "CASA DI LUSSO Signature",
        "lu_approuve": "Read and Approved",
        "days": "days",
        "per_day": "%/day",
        "not_specified": "Not specified",
    },
}


def _set_cell_bg(cell, hex_color: str):
    """Set table cell background color via OOXML."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def _set_cell_border_bottom(cell, color: str = "CCCCCC"):
    """Add a thin bottom border to a cell."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "4")
    bottom.set(qn("w:space"), "0")
    bottom.set(qn("w:color"), color)
    tcBorders.append(bottom)
    tcPr.append(tcBorders)


class ContractDOCGenerator:
    """Generate a python-docx DOCX for a Contract instance."""

    def __init__(self, contract, language: str = "fr"):
        self.contract = contract
        self.language = language if language in DOC_LABELS else "fr"
        self.labels = DOC_LABELS[self.language]
        self.doc = Document()
        self._configure_page()

    def _(self, key: str) -> str:
        return self.labels.get(key, key)

    def _configure_page(self):
        """Set narrow margins."""
        section = self.doc.sections[0]
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(1.8)
        section.right_margin = Cm(1.8)

    def _add_heading(self, text: str, level: int = 1):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(16) if level == 1 else Pt(12)
        run.font.color.rgb = BRAND_COLOR
        return p

    def _add_section_header(self, text: str):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(f"  {text}  ")
        run.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        # Set paragraph shading to brand color
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "1A2E4A")
        pPr.append(shd)
        return p

    def _add_info_table(self, rows: list[tuple[str, str]]):
        """Add a two-column label/value table."""
        table = self.doc.add_table(rows=len(rows), cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        table.style = "Table Grid"
        col_widths = [Cm(5), Cm(12.5)]
        for i, (label, value) in enumerate(rows):
            row = table.rows[i]
            row.cells[0].width = col_widths[0]
            row.cells[1].width = col_widths[1]
            # Alternating row background
            bg = "F5F5F5" if i % 2 == 0 else "FFFFFF"
            _set_cell_bg(row.cells[0], bg)
            _set_cell_bg(row.cells[1], bg)
            _set_cell_border_bottom(row.cells[0])
            _set_cell_border_bottom(row.cells[1])
            # Label cell
            lp = row.cells[0].paragraphs[0]
            lr = lp.add_run(label)
            lr.bold = True
            lr.font.size = Pt(9)
            # Value cell
            vp = row.cells[1].paragraphs[0]
            vr = vp.add_run(str(value) if value else self._("not_specified"))
            vr.font.size = Pt(9)
        self.doc.add_paragraph()  # spacing after table

    def _add_ref_row(self):
        """Header row with Ref / Date / Status."""
        c = self.contract
        table = self.doc.add_table(rows=1, cols=3)
        table.alignment = WD_TABLE_ALIGNMENT.LEFT
        table.style = "Table Grid"
        cells = table.rows[0].cells
        _set_cell_bg(cells[0], "F5F5F5")
        _set_cell_bg(cells[1], "F5F5F5")
        _set_cell_bg(cells[2], "F5F5F5")
        date_str = c.date_contrat.strftime("%d/%m/%Y") if c.date_contrat else "-"

        def _fill(cell, label, value):
            p = cell.paragraphs[0]
            r_label = p.add_run(f"{label}: ")
            r_label.bold = True
            r_label.font.size = Pt(9)
            r_val = p.add_run(value)
            r_val.font.size = Pt(9)

        _fill(cells[0], self._("ref"), c.numero_contrat)
        _fill(cells[1], self._("date"), date_str)
        _fill(cells[2], self._("statut"), c.statut)
        self.doc.add_paragraph()

    def _build(self):
        c = self.contract
        doc = self.doc

        # Title
        self._add_heading("CASA DI LUSSO", 1)
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(self._("title"))
        run.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = ACCENT_COLOR

        # Horizontal rule substitute — thin colored paragraph border
        hr = doc.add_paragraph()
        hr.paragraph_format.space_after = Pt(6)
        pPr = hr._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        bottom_bdr = OxmlElement("w:bottom")
        bottom_bdr.set(qn("w:val"), "single")
        bottom_bdr.set(qn("w:sz"), "6")
        bottom_bdr.set(qn("w:space"), "1")
        bottom_bdr.set(qn("w:color"), "C9A84C")
        pBdr.append(bottom_bdr)
        pPr.append(pBdr)

        # Ref / Date / Status
        self._add_ref_row()

        # ── Section 1: Client ──────────────────────────────────────────
        self._add_section_header(self._("section_client"))
        self._add_info_table(
            [
                (self._("nom"), c.client_nom),
                (self._("cin"), c.client_cin),
                (self._("qualite"), c.client_qualite),
                (self._("adresse"), c.client_adresse),
                (self._("tel"), c.client_tel),
                (self._("email"), c.client_email),
                (self._("ville_sig"), c.ville_signature),
            ]
        )

        # ── Section 2: Project ─────────────────────────────────────────
        self._add_section_header(self._("section_project"))
        services_text = (
            ", ".join(c.services)
            if isinstance(c.services, list)
            else str(c.services or "")
        )
        self._add_info_table(
            [
                (self._("adresse_tx"), c.adresse_travaux),
                (self._("type_bien"), c.type_bien),
                (self._("surface"), f"{c.surface} m²" if c.surface else None),
                (self._("services"), services_text or None),
                (self._("description"), c.description_travaux),
                (
                    self._("date_debut"),
                    c.date_debut.strftime("%d/%m/%Y") if c.date_debut else None,
                ),
                (self._("duree"), c.duree_estimee),
                (self._("acces"), c.conditions_acces),
            ]
        )

        # ── Section 3: Financial ───────────────────────────────────────
        self._add_section_header(self._("section_financial"))
        montant_ht = float(c.montant_ht)
        tva_pct = float(c.tva)
        montant_tva = montant_ht * tva_pct / 100
        montant_ttc = montant_ht + montant_tva
        tranches_text = ""
        if isinstance(c.tranches, list) and c.tranches:
            tranches_text = " | ".join(
                f"{t.get('label', '')}: {t.get('pourcentage', '')}%" for t in c.tranches
            )
        self._add_info_table(
            [
                (self._("montant_ht"), f"{montant_ht:,.2f} {c.devise}"),
                (self._("tva"), f"{tva_pct}%"),
                (self._("montant_ttc"), f"{montant_ttc:,.2f} {c.devise}"),
                (self._("tranches"), tranches_text or None),
                (self._("mode_paiement"), c.mode_paiement_texte),
                (self._("rib"), c.rib),
                (
                    self._("delai_retard"),
                    (
                        f"{c.delai_retard} {self._('days')}"
                        if c.delai_retard is not None
                        else None
                    ),
                ),
                (
                    self._("penalite"),
                    (
                        f"{c.penalite_retard} {self._('per_day')}"
                        if c.penalite_retard is not None
                        else None
                    ),
                ),
                (
                    self._("frais_redemarrage"),
                    (
                        f"{float(c.frais_redemarrage):,.2f} {c.devise}"
                        if c.frais_redemarrage
                        else None
                    ),
                ),
            ]
        )

        # ── Section 4: Clauses ─────────────────────────────────────────
        self._add_section_header(self._("section_clauses"))
        clauses_text = ""
        if isinstance(c.clauses_actives, list) and c.clauses_actives:
            clauses_text = "\n".join(f"• {cl}" for cl in c.clauses_actives)
        self._add_info_table(
            [
                (self._("garantie"), c.garantie),
                (
                    self._("delai_reserves"),
                    (
                        f"{c.delai_reserves} {self._('days')}"
                        if c.delai_reserves is not None
                        else None
                    ),
                ),
                (self._("tribunal"), c.tribunal),
                (self._("clauses"), clauses_text or None),
                (self._("clause_spec"), c.clause_spec),
                (self._("exclusions"), c.exclusions),
            ]
        )

        # ── Section 5: Options ─────────────────────────────────────────
        self._add_section_header(self._("section_options"))
        self._add_info_table(
            [
                (self._("type_contrat"), c.get_type_contrat_display()),
                (self._("responsable"), c.responsable_projet),
                (self._("architecte"), c.architecte),
                (self._("confidentialite"), c.confidentialite),
                (self._("version"), c.version_document),
                (self._("annexes"), c.annexes),
            ]
        )

        # ── Signatures ─────────────────────────────────────────────────
        self._add_section_header(self._("section_signatures"))
        doc.add_paragraph()
        sig_table = doc.add_table(rows=3, cols=2)
        sig_table.alignment = WD_TABLE_ALIGNMENT.LEFT
        sig_table.style = "Table Grid"

        # Header row
        for j, label_key in enumerate(["signature_client", "signature_cdl"]):
            cell = sig_table.rows[0].cells[j]
            _set_cell_bg(cell, "1A2E4A")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(self._(label_key))
            r.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            r.font.size = Pt(9)

        # Blank space row
        for j in range(2):
            cell = sig_table.rows[1].cells[j]
            cell.height = Cm(3)

        # Footer row
        sig_table.rows[2].cells[0].paragraphs[0].add_run(
            self._("lu_approuve")
        ).font.size = Pt(8)
        sig_table.rows[2].cells[1].paragraphs[0].add_run(
            c.responsable_projet or "CASA DI LUSSO"
        ).font.size = Pt(8)

    def generate_response(self) -> HttpResponse:
        self._build()
        buffer = BytesIO()
        self.doc.save(buffer)
        buffer.seek(0)
        filename = f"contrat_{self.contract.numero_contrat.replace('/', '-')}.docx"
        response = HttpResponse(
            buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
