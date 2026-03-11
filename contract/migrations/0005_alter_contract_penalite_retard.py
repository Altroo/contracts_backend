# Generated manually on 2026-03-11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contract", "0004_alter_contract_unique_together_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contract",
            name="penalite_retard",
            field=models.DecimalField(
                decimal_places=2,
                default=500,
                max_digits=10,
                verbose_name="Pénalité retard (MAD/j)",
            ),
        ),
    ]
