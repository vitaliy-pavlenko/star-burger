from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Place(models.Model):
    address = models.CharField(max_length=200, verbose_name='Адрес', unique=True)
    latitude = models.FloatField(
        validators=[
            MinValueValidator(-90.0),
            MaxValueValidator(90.0)
        ],
        null=True,
        verbose_name='Широта'
    )
    longitude = models.FloatField(
        validators=[
            MinValueValidator(-180.0),
            MaxValueValidator(180.0)
        ],
        null=True,
        verbose_name='Долгота'
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления', db_index=True)
