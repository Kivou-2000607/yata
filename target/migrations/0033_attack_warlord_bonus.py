# Generated by Django 4.0.5 on 2023-01-03 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("target", "0032_attack_ranked_war"),
    ]

    operations = [
        migrations.AddField(
            model_name="attack",
            name="warlord_bonus",
            field=models.FloatField(default=1.0),
        ),
    ]