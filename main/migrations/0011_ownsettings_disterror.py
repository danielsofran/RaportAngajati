# Generated by Django 4.0.6 on 2022-07-20 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_remove_ownsettings_forme_ownsettings_program_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ownsettings',
            name='disterror',
            field=models.FloatField(default=10, verbose_name='Distanta in metrii acceptata ca eroare a calculului de locatie'),
        ),
    ]
