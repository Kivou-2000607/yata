# Generated by Django 2.0.7 on 2020-01-14 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chain', '0099_auto_20200112_1406'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stat',
            name='type',
        ),
    ]
