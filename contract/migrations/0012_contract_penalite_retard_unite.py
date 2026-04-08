from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("contract", "0011_historicalproject"),
    ]

    operations = [
        migrations.AddField(
            model_name="contract",
            name="penalite_retard_unite",
            field=models.CharField(
                choices=[
                    ("mad_per_day", "MAD par jour"),
                    ("percent_per_day", "Pourcentage par jour"),
                ],
                default="mad_per_day",
                max_length=20,
                verbose_name="Unité pénalité retard",
            ),
        ),
        migrations.AddField(
            model_name="historicalcontract",
            name="penalite_retard_unite",
            field=models.CharField(
                choices=[
                    ("mad_per_day", "MAD par jour"),
                    ("percent_per_day", "Pourcentage par jour"),
                ],
                default="mad_per_day",
                max_length=20,
                verbose_name="Unité pénalité retard",
            ),
        ),
    ]
