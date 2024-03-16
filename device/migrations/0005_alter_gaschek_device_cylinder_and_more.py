# Generated by Django 5.0.2 on 2024-02-15 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0004_alter_gaschek_device_alarm_alter_gaschek_device_call_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gaschek_device',
            name='cylinder',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='gaschek_device',
            name='gas_mass',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=10),
        ),
    ]
