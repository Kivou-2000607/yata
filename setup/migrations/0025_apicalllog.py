from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("setup", "0024_delete_analytics_delete_apicalllog_delete_balance_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApiCallLog",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("timestamp", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("section", models.CharField(db_index=True, max_length=64)),
                ("is_error", models.BooleanField(default=False)),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
    ]
