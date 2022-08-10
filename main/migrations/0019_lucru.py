# Generated by Django 4.0.6 on 2022-08-08 07:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_alter_user_telefon'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lucru',
            fields=[
                ('info_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main.info')),
                ('denumire', models.TextField(max_length=300, verbose_name='lucru')),
            ],
            options={
                'verbose_name_plural': 'Lucrari',
            },
            bases=('main.info',),
        ),
    ]