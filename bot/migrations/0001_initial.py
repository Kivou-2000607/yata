# Generated by Django 2.0 on 2019-11-03 22:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('player', '0025_player_did'),
    ]

    operations = [
        migrations.CreateModel(
            name='BotData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default='BOT_TOKEN', max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eventId', models.IntegerField(default=0)),
                ('timestamp', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Preference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('yataServer', models.BooleanField(default=False)),
                ('yataServerName', models.CharField(blank=True, default='', max_length=32)),
                ('notificationsEvents', models.BooleanField(default=False)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='player.Player')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='preference',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.Preference'),
        ),
    ]
