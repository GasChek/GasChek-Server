# Generated by Django 4.1.5 on 2023-02-12 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_delivery_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='gas_orders',
            name='delivery',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
