# Generated by Django 4.0.6 on 2022-07-20 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_forma_nume'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ownsettings',
            name='forme',
        ),
        migrations.AddField(
            model_name='ownsettings',
            name='program',
            field=models.CharField(default='L Ma Mi J V S D', max_length=20),
        ),
        migrations.AlterField(
            model_name='forma',
            name='nume',
            field=models.CharField(blank=True, default='corp', max_length=15),
        ),
    ]
