# Generated by Django 4.1.5 on 2023-02-13 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('esp32', '0002_gas_leakage_action'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gas_leakage',
            name='action',
            field=models.CharField(max_length=15),
        ),
    ]
