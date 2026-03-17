from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("setup", "0027_apicalllog_caller"),
    ]

    operations = [
        migrations.AddField(
            model_name="apicalllog",
            name="player_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
