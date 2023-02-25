# Generated by Django 4.1.5 on 2023-02-04 22:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0008_alter_gaschek_device_alarm_alter_gaschek_device_call_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gas_orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cylinder', models.CharField(max_length=10)),
                ('price', models.IntegerField()),
                ('reference', models.CharField(max_length=50)),
                ('gas_dealer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='accounts.gas_dealer')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='Cylinder_Price',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('cylinder', models.IntegerField()),
                ('price', models.IntegerField()),
                ('gas_dealer', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='accounts.gas_dealer')),
            ],
            options={
                'ordering': ['gas_dealer'],
            },
        ),
    ]
