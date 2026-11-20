from datetime import date, timedelta
from unittest.mock import patch
from types import SimpleNamespace
import pytest
from django.core.cache import cache
from django.utils import timezone
from ai_assistant.models import PdfTextTranslation
from ai_assistant.pdf_translation import (
    ensure_sources,
    load_pdf_translations,
    source,
    validate_saved_translation,
)
from ai_assistant.tasks import (
    prepare_contract_pdf,
    translate_pending_pdf_texts,
    backfill_pdf_translations,
    quota_key,
)
from ai_assistant.client import AiAssistantClient
from ai_assistant.exceptions import (
    PdfTranslationPending,
    PdfTranslationDeferred,
    InvalidModelResponse,
)
from contract.models import Contract
from contract.ai_pdf import contract_pdf_sources

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def preparation_settings(settings):
    settings.AI_PDF_TRANSLATION_ENABLED = True
    settings.CELERY_TASK_ALWAYS_EAGER = False
    cache.clear()
    with patch(
        "ai_assistant.pdf_translation.dispatch_pending"
    ) as dispatch, patch.object(translate_pending_pdf_texts, "apply_async"):
        yield dispatch


def test_contract_save_queues_only_after_commit_without_model_calls(
    django_capture_on_commit_callbacks, preparation_settings
):
    with patch.object(
        AiAssistantClient, "translate_many"
    ) as model, django_capture_on_commit_callbacks(execute=True):
        contract = Contract.objects.create(
            numero_contrat="QA-01",
            date_contrat=date.today(),
            description_travaux="Pose de carrelage",
        )
        assert (
            PdfTextTranslation.objects.filter(source_text="Pose de carrelage").count()
            == 2
        )
        preparation_settings.assert_not_called()
    preparation_settings.assert_called_once()
    model.assert_not_called()


def test_preparation_covers_json_duration_and_preserves_names():
    contract = Contract.objects.create(
        numero_contrat="QA-02",
        date_contrat=date.today(),
        description_travaux="Travaux Client QA",
        client_nom="Client QA",
        prestations=[
            {
                "nom": "Carrelage",
                "description": "Pose 120*120cm",
                "unite": "m²",
                "quantite": 2,
            }
        ],
        tranches=[{"label": "À la commande", "pourcentage": 50}],
        duree_estimee="10 jours",
    )
    prepare_contract_pdf(contract.pk)
    specs = contract_pdf_sources(contract)
    assert {"Pose 120*120cm", "m²", "10 jours", "À la commande"}.issubset(
        {spec.text for spec in specs}
    )
    assert next(spec for spec in specs if "Client QA" in spec.text).protected_terms == (
        "Client QA",
    )
    assert set(PdfTextTranslation.objects.values_list("language", flat=True)) == {
        "fr",
        "en",
    }
    assert not PdfTextTranslation.objects.filter(source_text="50").exists()


def test_new_or_edited_pdf_text_never_uses_an_old_cached_value():
    spec = source("Livrer avant midi")
    ensure_sources("casa_di_lusso", [spec], ["en"], dispatch=False)
    with pytest.raises(PdfTranslationPending):
        load_pdf_translations("casa_di_lusso", [spec], "en")
    PdfTextTranslation.objects.update(
        status="ready", translated_text="Deliver before noon"
    )
    with patch.object(AiAssistantClient, "translate_many") as model:
        assert (
            load_pdf_translations("casa_di_lusso", [spec], "en")[spec.text]
            == "Deliver before noon"
        )
    model.assert_not_called()
    with pytest.raises(PdfTranslationPending):
        load_pdf_translations("casa_di_lusso", [source("Livrer après midi")], "en")
    with pytest.raises(PdfTranslationPending):
        load_pdf_translations("blueline", [spec], "en")


def test_worker_persists_valid_text_and_rejects_broken_layout():
    spec = source("• Livrer 120*120cm.\n• Marbre non compris.")
    ensure_sources("casa_di_lusso", [spec], ["en"], dispatch=False)
    with patch.object(
        AiAssistantClient,
        "translate_many",
        return_value={spec.text: "• Deliver 120*120cm.\n• Marble not included."},
    ) as client:
        translate_pending_pdf_texts()
    assert PdfTextTranslation.objects.get().status == "ready"
    assert client.call_args.kwargs["retry_rate_limit"] is False
    assert client.call_args.kwargs["context"] == "contract_pdf"
    row = PdfTextTranslation.objects.get()
    for broken in [
        "Deliver 120*120cm. Marble not included.",
        "• Deliver 120x120cm.\n• Marble not included.",
        "• Deliver 120*120cm.\n• Marble included.",
    ]:
        with pytest.raises(InvalidModelResponse):
            validate_saved_translation(row, broken)


def test_quota_deadlines_do_not_extend_and_foreground_can_use_reserved_capacity():
    from rest_framework.exceptions import Throttled

    ensure_sources(
        "casa_di_lusso",
        [source("Chaise en bois")],
        ["en"],
        priority=100,
        dispatch=False,
    )
    with patch.object(
        AiAssistantClient, "translate_many", side_effect=Throttled(wait=60)
    ):
        translate_pending_pdf_texts()
    deadline = cache.get(quota_key(100))
    ensure_sources(
        "casa_di_lusso", [source("Table en bois")], ["en"], priority=100, dispatch=False
    )
    for _ in range(10):
        translate_pending_pdf_texts()
    assert cache.get(quota_key(100)) == deadline
    ensure_sources(
        "casa_di_lusso", [source("Lampe en bois")], ["en"], priority=0, dispatch=False
    )
    with patch.object(
        AiAssistantClient,
        "translate_many",
        return_value={"Lampe en bois": "Wooden lamp"},
    ):
        translate_pending_pdf_texts()
    assert PdfTextTranslation.objects.get(source_text="Lampe en bois").status == "ready"
    assert not PdfTextTranslation.objects.exclude(attempts=0).exists()


def test_quota_deferred_pdf_does_not_wait_for_sync_translation():
    spec = source("Livrer avant midi")
    ensure_sources("casa_di_lusso", [spec], ["en"], priority=0, dispatch=False)
    PdfTextTranslation.objects.update(
        last_error="ai_gateway_throttled", available_at=timezone.now() + timedelta(seconds=60)
    )
    with pytest.raises(PdfTranslationDeferred):
        load_pdf_translations("casa_di_lusso", [spec], "en")


def test_worker_recovers_legacy_quota_wait():
    spec = source("Livrer avant midi")
    ensure_sources("casa_di_lusso", [spec], ["en"], priority=0, dispatch=False)
    postponed = timezone.now() + timedelta(hours=6)
    PdfTextTranslation.objects.update(last_error="ai_rate_limited", available_at=postponed)
    cache.set("pdf-translation-quota:foreground", postponed.timestamp(), 21600)
    with patch.object(
        AiAssistantClient, "translate_many", return_value={spec.text: "Deliver before noon"}
    ):
        translate_pending_pdf_texts()
    assert load_pdf_translations("casa_di_lusso", [spec], "en") == {spec.text: "Deliver before noon"}


def test_backfill_is_bounded_idempotent_and_in_background(settings):
    settings.AI_PDF_TRANSLATION_ENABLED = False
    for n in range(3):
        Contract.objects.create(
            numero_contrat=f"QA-{n}",
            date_contrat=date.today(),
            description_travaux=f"Travaux {n}",
        )
    settings.AI_PDF_TRANSLATION_ENABLED = True
    with patch.object(backfill_pdf_translations, "apply_async") as next_job:
        assert backfill_pdf_translations(batch_size=2)["scanned"] == 2
        backfill_pdf_translations(batch_size=2)
    assert PdfTextTranslation.objects.count() == 4
    assert set(PdfTextTranslation.objects.values_list("priority", flat=True)) == {100}
    assert next_job.call_args.kwargs["kwargs"]["after_pk"] > 0


def test_pdf_html_keeps_nested_bullet_indentation_and_plain_text():
    from contract.pdf import _esc

    assert _esc("• A & B\n  • <Suite>") == "• A &amp; B<br>&#160;&#160;• &lt;Suite&gt;"


def test_rolled_back_save_leaves_no_translation_work(
    django_capture_on_commit_callbacks, preparation_settings
):
    from django.db import transaction

    with django_capture_on_commit_callbacks(execute=True):
        with pytest.raises(ValueError), transaction.atomic():
            Contract.objects.create(
                numero_contrat="QA-ROLLBACK",
                date_contrat=date.today(),
                description_travaux="Travaux annulés",
            )
            raise ValueError("rollback")
    assert not PdfTextTranslation.objects.exists()
    preparation_settings.assert_not_called()


def test_pdf_scheduler_does_not_activate_or_change_notification_schedules():
    from contracts_backend.celery_conf import app as main

    previous = dict(main.conf.beat_schedule)
    from ai_assistant.pdf_beat import app as scheduler

    assert scheduler is not main
    assert set(scheduler.conf.beat_schedule) == {"prepare-pending-pdf-translations"}
    assert dict(main.conf.beat_schedule) == previous


def test_company_representative_role_is_prepared_and_not_left_in_french():
    from core.models import CompanyConfig
    from contract.st_pdf import SousTraitancePDFGenerator

    config = CompanyConfig.objects.create(
        company="casa_di_lusso",
        name="Company QA",
        qualite_representant="Directeur général",
    )
    instance = Contract.objects.create(
        numero_contrat="QA-ST",
        date_contrat=date.today(),
        company=config.company,
        contract_category="sous_traitance",
    )
    assert "Directeur général" in {spec.text for spec in contract_pdf_sources(instance)}
    PdfTextTranslation.objects.filter(
        source_text="Directeur général", language="en"
    ).update(status="ready", translated_text="Managing Director")
    with patch.object(AiAssistantClient, "translate_many") as model:
        output = SousTraitancePDFGenerator(instance, language="en")
        assert output.ep.qualite_representant == "Managing Director"
    model.assert_not_called()
    config.refresh_from_db()
    assert config.qualite_representant == "Directeur général"


def test_original_english_contract_parties_remain_valid():
    row = SimpleNamespace(
        source_text="The project owner appoints the contractor.",
        protected_terms=[],
        language="en",
    )
    validate_saved_translation(row, row.source_text)



def test_french_pdf_uses_original_source_before_reading_translation_rows():
    value = "Location STORE N° 42"
    with patch.object(PdfTextTranslation.objects, "filter") as lookup:
        assert load_pdf_translations("casa_di_lusso", [source(value)], "fr") == {value: value}

    lookup.assert_not_called()
