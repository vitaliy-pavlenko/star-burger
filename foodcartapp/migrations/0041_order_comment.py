# Generated by Django 3.2 on 2021-11-03 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20211103_1521'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, max_length=300, verbose_name='Комментарий к заказу'),
        ),
    ]
