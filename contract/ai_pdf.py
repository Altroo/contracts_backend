from copy import copy, deepcopy
from django.conf import settings
from ai_assistant.client import AiAssistantClient

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


def translated_contract(contract, language):
    if not getattr(settings, "AI_PDF_TRANSLATION_ENABLED", False):
        return contract
    result = copy(contract)
    texts = [getattr(contract, field, "") for field in TEXT_FIELDS]
    for field, keys in JSON_FIELDS.items():
        value = getattr(contract, field, None)
        if isinstance(value, list):
            setattr(result, field, deepcopy(value))
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
    translated = AiAssistantClient().translate_many(
        texts,
        target_language=language,
        protected_terms=[str(p) for p in protected if p and len(str(p)) <= 200],
        context="contract_pdf",
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
