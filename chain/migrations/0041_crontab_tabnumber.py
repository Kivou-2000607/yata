# Generated by Django 2.0.5 on 2019-05-14 09:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chain', '0040_auto_20190514_0849'),
    ]

    operations = [
        migrations.AddField(
            model_name='crontab',
            name='tabNumber',
            field=models.IntegerField(default=0),
        ),
    ]
