# Generated by Django 3.1.2 on 2021-01-04 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0022_companystock_delta_positions'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='effectiveness_merits',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='companydata',
            name='effectiveness_merits',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='employee',
            name='effectiveness_merits',
            field=models.IntegerField(default=0),
        ),
    ]
