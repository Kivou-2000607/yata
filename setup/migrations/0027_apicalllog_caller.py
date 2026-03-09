from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("setup", "0026_apicalllog_error_code"),
    ]

    operations = [
        migrations.AddField(
            model_name="apicalllog",
            name="caller",
            field=models.CharField(blank=True, default="", max_length=128),
        ),
    ]
