from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contract", "0006_alter_contract_garantie_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contract",
            name="st_lot_type",
            field=models.JSONField(
                blank=True,
                default=list,
                null=True,
                verbose_name="Type(s) de lot",
            ),
        ),
        migrations.AlterField(
            model_name="contract",
            name="st_type_prix",
            field=models.JSONField(
                blank=True,
                default=list,
                null=True,
                verbose_name="Type(s) de prix",
            ),
        ),
        migrations.AlterField(
            model_name="contract",
            name="st_penalite_taux",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="Pénalité retard (MAD/jour)",
            ),
        ),
    ]
