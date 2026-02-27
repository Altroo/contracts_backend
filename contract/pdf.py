from io import BytesIO

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BRAND_COLOR = colors.HexColor("#1a2e4a")
ACCENT_COLOR = colors.HexColor("#c9a84c")
LIGHT_GRAY = colors.HexColor("#f5f5f5")
BORDER_GRAY = colors.HexColor("#cccccc")


def _build_styles():
    styles = getSampleStyleSheet()
    custom = {
        "Title": ParagraphStyle(
            "Title",
            fontName="Helvetica-Bold",
            fontSize=18,
            textColor=BRAND_COLOR,
            alignment=TA_CENTER,
            spaceAfter=4,
        ),
        "SubTitle": ParagraphStyle(
            "SubTitle",
            fontName="Helvetica",
            fontSize=10,
            textColor=ACCENT_COLOR,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "SectionHeader": ParagraphStyle(
            "SectionHeader",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=colors.white,
            backColor=BRAND_COLOR,
            spaceAfter=4,
            spaceBefore=8,
            leftIndent=4,
            rightIndent=4,
            leading=14,
        ),
        "Normal": ParagraphStyle(
            "Normal",
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            spaceAfter=2,
        ),
        "Bold": ParagraphStyle(
            "Bold",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=12,
            spaceAfter=2,
        ),
        "Small": ParagraphStyle(
            "Small",
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=colors.HexColor("#555555"),
        ),
        "Right": ParagraphStyle(
            "Right",
            fontName="Helvetica",
            fontSize=8.5,
            alignment=TA_RIGHT,
            leading=12,
        ),
        "Amount": ParagraphStyle(
            "Amount",
            fontName="Helvetica-Bold",
            fontSize=11,
            alignment=TA_RIGHT,
            textColor=BRAND_COLOR,
        ),
    }
    return custom


LABELS = {
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
        "surface": "Area (m\u00b2)",
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


class ContractPDFGenerator:
    """Generate a ReportLab PDF for a Contract instance."""

    def __init__(self, contract, language: str = "fr"):
        self.contract = contract
        self.language = language if language in LABELS else "fr"
        self.labels = LABELS[self.language]
        self.styles = _build_styles()

    def _(self, key: str) -> str:
        return self.labels.get(key, key)

    def _p(self, text: str, style: str = "Normal") -> Paragraph:
        return Paragraph(str(text) if text else "", self.styles[style])

    def _section(self, title: str) -> Paragraph:
        return Paragraph(f"  {title}", self.styles["SectionHeader"])

    def _row(self, label: str, value) -> list:
        val = (
            str(value)
            if value is not None and str(value).strip()
            else self._("not_specified")
        )
        return [self._p(f"<b>{label}</b>"), self._p(val)]

    def _info_table(self, rows: list) -> Table:
        table = Table(rows, colWidths=[5 * cm, 13 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT_GRAY]),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.25, BORDER_GRAY),
                ]
            )
        )
        return table

    def _build_content(self) -> list:
        c = self.contract
        elements = []

        # ── Header ──────────────────────────────────────────────────────
        elements.append(self._p("CASA DI LUSSO", "Title"))
        elements.append(self._p(self._("title"), "SubTitle"))
        elements.append(
            HRFlowable(width="100%", thickness=2, color=ACCENT_COLOR, spaceAfter=8)
        )

        # Ref / Date / Status row
        ref_table = Table(
            [
                [
                    self._p(f"<b>{self._('ref')}:</b> {c.numero_contrat}"),
                    self._p(
                        f"<b>{self._('date')}:</b> {c.date_contrat.strftime('%d/%m/%Y') if c.date_contrat else '-'}"
                    ),
                    self._p(f"<b>{self._('statut')}:</b> {c.statut}"),
                ]
            ],
            colWidths=[6 * cm, 6 * cm, 6 * cm],
        )
        ref_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER_GRAY),
                ]
            )
        )
        elements.append(ref_table)
        elements.append(Spacer(1, 0.3 * cm))

        # ── Section 1: Client ────────────────────────────────────────────
        elements.append(self._section(self._("section_client")))
        elements.append(
            self._info_table(
                [
                    self._row(self._("nom"), c.client_nom),
                    self._row(self._("cin"), c.client_cin),
                    self._row(self._("qualite"), c.client_qualite),
                    self._row(self._("adresse"), c.client_adresse),
                    self._row(self._("tel"), c.client_tel),
                    self._row(self._("email"), c.client_email),
                    self._row(self._("ville_sig"), c.ville_signature),
                ]
            )
        )
        elements.append(Spacer(1, 0.2 * cm))

        # ── Section 2: Project ───────────────────────────────────────────
        elements.append(self._section(self._("section_project")))
        services_text = (
            ", ".join(c.services)
            if isinstance(c.services, list)
            else str(c.services or "")
        )
        elements.append(
            self._info_table(
                [
                    self._row(self._("adresse_tx"), c.adresse_travaux),
                    self._row(self._("type_bien"), c.type_bien),
                    self._row(
                        self._("surface"), f"{c.surface} m²" if c.surface else None
                    ),
                    self._row(self._("services"), services_text or None),
                    self._row(self._("description"), c.description_travaux),
                    self._row(
                        self._("date_debut"),
                        c.date_debut.strftime("%d/%m/%Y") if c.date_debut else None,
                    ),
                    self._row(self._("duree"), c.duree_estimee),
                    self._row(self._("acces"), c.conditions_acces),
                ]
            )
        )
        elements.append(Spacer(1, 0.2 * cm))

        # ── Section 3: Financial ─────────────────────────────────────────
        elements.append(self._section(self._("section_financial")))
        tva_pct = c.tva
        montant_ht = float(c.montant_ht)
        montant_tva = montant_ht * float(tva_pct) / 100
        montant_ttc = montant_ht + montant_tva

        tranches_text = ""
        if isinstance(c.tranches, list) and c.tranches:
            tranches_text = " | ".join(
                f"{t.get('label', '')}: {t.get('pourcentage', '')}%" for t in c.tranches
            )

        elements.append(
            self._info_table(
                [
                    self._row(
                        self._("montant_ht"),
                        f"{montant_ht:,.2f} {c.devise}",
                    ),
                    self._row(self._("tva"), f"{tva_pct}%"),
                    self._row(
                        self._("montant_ttc"),
                        f"{montant_ttc:,.2f} {c.devise}",
                    ),
                    self._row(self._("tranches"), tranches_text or None),
                    self._row(self._("mode_paiement"), c.mode_paiement_texte),
                    self._row(self._("rib"), c.rib),
                    self._row(
                        self._("delai_retard"),
                        (
                            f"{c.delai_retard} {self._('days')}"
                            if c.delai_retard is not None
                            else None
                        ),
                    ),
                    self._row(
                        self._("penalite"),
                        (
                            f"{c.penalite_retard} {self._('per_day')}"
                            if c.penalite_retard is not None
                            else None
                        ),
                    ),
                    self._row(
                        self._("frais_redemarrage"),
                        (
                            f"{float(c.frais_redemarrage):,.2f} MAD"
                            if c.frais_redemarrage
                            else None
                        ),
                    ),
                ]
            )
        )
        elements.append(Spacer(1, 0.2 * cm))

        # ── Section 4: Clauses ───────────────────────────────────────────
        elements.append(self._section(self._("section_clauses")))
        clauses_text = ""
        if isinstance(c.clauses_actives, list) and c.clauses_actives:
            clauses_text = "\n".join(f"• {cl}" for cl in c.clauses_actives)

        elements.append(
            self._info_table(
                [
                    self._row(self._("garantie"), c.garantie),
                    self._row(
                        self._("delai_reserves"),
                        (
                            f"{c.delai_reserves} {self._('days')}"
                            if c.delai_reserves is not None
                            else None
                        ),
                    ),
                    self._row(self._("tribunal"), c.tribunal),
                    self._row(self._("clauses"), clauses_text or None),
                    self._row(self._("clause_spec"), c.clause_spec),
                    self._row(self._("exclusions"), c.exclusions),
                ]
            )
        )
        elements.append(Spacer(1, 0.2 * cm))

        # ── Section 5: Options ───────────────────────────────────────────
        elements.append(self._section(self._("section_options")))
        elements.append(
            self._info_table(
                [
                    self._row(self._("type_contrat"), c.get_type_contrat_display()),
                    self._row(self._("responsable"), c.responsable_projet),
                    self._row(self._("architecte"), c.architecte),
                    self._row(self._("confidentialite"), c.confidentialite),
                    self._row(self._("version"), c.version_document),
                    self._row(self._("annexes"), c.annexes),
                ]
            )
        )
        elements.append(Spacer(1, 0.5 * cm))

        # ── Signatures ───────────────────────────────────────────────────
        elements.append(self._section(self._("section_signatures")))
        elements.append(Spacer(1, 0.3 * cm))
        sig_table = Table(
            [
                [
                    self._p(f"<b>{self._('signature_client')}</b>"),
                    self._p(f"<b>{self._('signature_cdl')}</b>"),
                ],
                [
                    Spacer(1, 2 * cm),
                    Spacer(1, 2 * cm),
                ],
                [
                    self._p(self._("lu_approuve"), "Small"),
                    self._p(c.responsable_projet or "CASA DI LUSSO", "Small"),
                ],
            ],
            colWidths=[9 * cm, 9 * cm],
        )
        sig_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("LINEBELOW", (0, 1), (-1, 1), 0.5, BORDER_GRAY),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(sig_table)

        return elements

    def generate_response(self) -> HttpResponse:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            title=f"Contrat {self.contract.numero_contrat}",
            author="CASA DI LUSSO",
        )
        story = self._build_content()
        doc.build(story)

        buffer.seek(0)
        filename = f"contrat_{self.contract.numero_contrat.replace('/', '-')}.pdf"
        response = HttpResponse(buffer.read(), content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{filename}"'
        return response
