from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("setup", "0025_apicalllog"),
    ]

    operations = [
        migrations.AddField(
            model_name="apicalllog",
            name="error_code",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
