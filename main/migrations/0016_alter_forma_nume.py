# Generated by Django 4.0.6 on 2022-07-28 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_alter_forma_tip_alter_info_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forma',
            name='nume',
            field=models.CharField(blank=True, default='corp', max_length=30),
        ),
    ]