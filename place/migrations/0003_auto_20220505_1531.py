# Generated by Django 3.2 on 2022-05-05 15:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('place', '0002_alter_place_updated_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='latitude',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(-90.0), django.core.validators.MaxValueValidator(90.0)], verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='place',
            name='longitude',
            field=models.FloatField(null=True, validators=[django.core.validators.MinValueValidator(-180.0), django.core.validators.MaxValueValidator(180.0)], verbose_name='Долгота'),
        ),
    ]
