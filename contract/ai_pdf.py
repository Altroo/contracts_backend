from copy import copy, deepcopy
from django.conf import settings
from ai_assistant.pdf_translation import load_pdf_translations, source

TEXT_FIELDS = (
    "description_travaux",
    "conditions_acces",
    "clause_spec",
    "exclusions",
    "annexes",
    "materiaux_detail",
    "exclusions_garantie",
    "notes",
    "st_lot_description",
    "st_observations",
    "st_qualite",
)
JSON_FIELDS = {
    "prestations": ("nom", "description", "desc", "unite"),
    "tranches": ("label",),
    "st_tranches": ("label",),
}


def contract_pdf_sources(contract):
    texts = [getattr(contract, field, "") for field in TEXT_FIELDS]
    for field, keys in JSON_FIELDS.items():
        value = getattr(contract, field, None)
        if isinstance(value, list):
            texts.extend(
                row.get(key, "")
                for row in value
                if isinstance(row, dict)
                for key in keys
            )
    duration = getattr(contract, "duree_estimee", "")
    if duration and not str(duration).isdigit():
        texts.append(duration)
    protected = [
        getattr(contract, key, "")
        for key in (
            "company",
            "numero_contrat",
            "client_nom",
            "responsable_projet",
            "architecte",
            "st_name",
            "st_rep",
            "st_banque",
        )
    ]
    project = getattr(contract, "st_projet", None)
    if project is not None:
        protected.extend(
            [getattr(project, "name", ""), getattr(project, "maitre_ouvrage", "")]
        )
    if getattr(contract, "contract_category", "") == "sous_traitance":
        from core.models import CompanyConfig

        config = CompanyConfig.objects.filter(company=contract.company).first()
        if config is not None:
            texts.append(config.qualite_representant)
            protected.extend([config.name, config.representant])
    display = getattr(contract, "get_company_display", None)
    if display:
        protected.append(display())
    return [
        spec
        for text in texts
        if (
            spec := source(
                text, [str(p) for p in protected if p and len(str(p)) <= 200]
            )
        )
    ]


def translated_contract(contract, language):
    if not getattr(settings, "AI_PDF_TRANSLATION_ENABLED", False):
        return contract
    result = copy(contract)
    for field in JSON_FIELDS:
        if isinstance(getattr(contract, field, None), list):
            setattr(result, field, deepcopy(getattr(contract, field)))
    duration = getattr(contract, "duree_estimee", "")
    translated = load_pdf_translations(
        str(getattr(contract, "company", "default")),
        contract_pdf_sources(contract),
        language,
    )
    for field in TEXT_FIELDS:
        value = getattr(contract, field, None)
        if isinstance(value, str):
            setattr(result, field, translated.get(value, value))
    if duration in translated:
        result.duree_estimee = translated[duration]
    for field, keys in JSON_FIELDS.items():
        value = getattr(result, field, None)
        if isinstance(value, list):
            for row in value:
                if isinstance(row, dict):
                    for key in keys:
                        if isinstance(row.get(key), str):
                            row[key] = translated.get(row[key], row[key])
    return result


def company_role_source(config):
    return source(str(config.qualite_representant), [config.name, config.representant])


def translated_company_role(config, language):
    value = str(config.qualite_representant)
    if not getattr(settings, "AI_PDF_TRANSLATION_ENABLED", False):
        return "Manager" if language == "en" and value == "Gérant" else value
    return load_pdf_translations(
        str(config.company), [company_role_source(config)], language
    )[value]
