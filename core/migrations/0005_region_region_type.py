# Generated by Django 5.1 on 2024-08-25 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_rename_continent_region_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='region_type',
            field=models.CharField(choices=[('continent', 'continent'), ('ocean', 'ocean')], default=0, max_length=16),
            preserve_default=False,
        ),
    ]
