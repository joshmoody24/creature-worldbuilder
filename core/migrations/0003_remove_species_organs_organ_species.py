# Generated by Django 5.1 on 2024-08-25 00:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_species_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='species',
            name='organs',
        ),
        migrations.AddField(
            model_name='organ',
            name='species',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='organs', to='core.species'),
            preserve_default=False,
        ),
    ]
