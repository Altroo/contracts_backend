from django.db.models.signals import post_save


def connect():
    from contract.models import Contract
    from core.models import CompanyConfig

    post_save.connect(
        prepare, sender=Contract, dispatch_uid="prepare_contract_pdf_texts"
    )

    post_save.connect(
        prepare_company_role,
        sender=CompanyConfig,
        dispatch_uid="prepare_company_pdf_role",
    )


def prepare(sender, instance, raw=False, update_fields=None, **kwargs):
    if raw:
        return
    from .pdf_translation import translation_enabled
    from .pdf_translation import ensure_sources
    from contract.ai_pdf import contract_pdf_sources
    from contract.ai_pdf import TEXT_FIELDS, JSON_FIELDS

    relevant = (
        set(TEXT_FIELDS)
        | set(JSON_FIELDS)
        | {
            "duree_estimee",
            "company",
            "client_nom",
            "numero_contrat",
            "responsable_projet",
            "architecte",
            "st_name",
            "st_rep",
            "st_banque",
            "st_projet",
        }
    )
    if translation_enabled() and (
        update_fields is None or relevant.intersection(update_fields)
    ):
        ensure_sources(str(instance.company), contract_pdf_sources(instance))


def prepare_company_role(sender, instance, raw=False, update_fields=None, **kwargs):
    if raw:
        return
    from .pdf_translation import translation_enabled, ensure_sources
    from contract.ai_pdf import company_role_source

    if translation_enabled() and (
        update_fields is None
        or set(update_fields).intersection(
            {"qualite_representant", "name", "representant", "company"}
        )
    ):
        spec = company_role_source(instance)
        if spec:
            ensure_sources(str(instance.company), [spec])
