from django.db import migrations


def record_release(apps, schema_editor):
    apps.get_model("ws", "ChangelogEntry").objects.using(
        schema_editor.connection.alias
    ).update_or_create(
        date="2026-11-17",
        defaults={
            "version": "2.12.4",
            "title_fr": "Traductions professionnelles et PDF plus rapides",
            "title_en": "Natural translations and faster PDFs",
            "changes_fr": "Traduction tenant compte du sens, correction grammaticale et reformulation professionnelle améliorées.\nRetours à la ligne, listes, noms, références, montants et unités conservés.\nPréparation des textes des contrats en arrière-plan lors des ajouts et modifications, sans bloquer l’enregistrement.\nLes PDF utilisent les traductions enregistrées. Indicateur de chargement et message d’attente clair pendant leur préparation.",
            "changes_en": "Improved meaning-aware translation, grammar correction and professional rewriting.\nPreserve line breaks, lists, names, references, amounts and units.\nPrepare contract text in the background after additions and edits without delaying saves.\nPDFs use saved translations, with loading feedback and a clear waiting message during preparation.",
            "is_published": False,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("ws", "0004_seed_changelog_history")]
    operations = [migrations.RunPython(record_release, migrations.RunPython.noop)]
