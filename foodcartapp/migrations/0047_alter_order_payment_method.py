# Generated by Django 3.2 on 2021-11-27 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_auto_20211127_0959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.IntegerField(choices=[(1, 'Оплата наличными'), (2, 'Оплата картой')], db_index=True, verbose_name='Способ оплаты'),
        ),
    ]