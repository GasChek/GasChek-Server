# Generated by Django 5.0.2 on 2024-02-15 13:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Gaschek_Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(max_length=50, unique=True)),
                ('password', models.CharField(max_length=50, unique=True)),
                ('alarm', models.CharField(choices=[('off', 'off'), ('on', 'on')], default='off', max_length=10)),
                ('call', models.CharField(choices=[('off', 'off'), ('on', 'on')], default='off', max_length=10)),
                ('text', models.CharField(choices=[('off', 'off'), ('on', 'on')], default='off', max_length=10)),
                ('indicator', models.CharField(choices=[('off', 'off'), ('on', 'on')], default='off', max_length=10)),
                ('cylinder', models.CharField(default='0kg', max_length=10)),
                ('gas_mass', models.FloatField(default='0', max_length=10)),
                ('gas_level', models.IntegerField(default=0)),
                ('battery_level', models.IntegerField(default=0)),
                ('country_code', models.CharField(blank=True, max_length=10)),
                ('phonenumber_gaschek_device_1', models.CharField(blank=True, max_length=25)),
                ('phonenumber_gaschek_device_2', models.CharField(blank=True, max_length=25)),
                ('phonenumber_gaschek_device_3', models.CharField(blank=True, max_length=25)),
                ('is_connected_with_device', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Gas_Leakage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=15)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('gaschek_device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='device.gaschek_device')),
            ],
        ),
    ]