# Generated by Django 4.0.6 on 2022-08-02 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_alter_info_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='telefon',
            field=models.CharField(blank=True, default='', max_length=15),
        ),
    ]