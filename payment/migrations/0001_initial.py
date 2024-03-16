# Generated by Django 5.0.2 on 2024-02-15 13:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_delete_gaschek_device'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('delivery', models.IntegerField()),
                ('reference', models.CharField(max_length=50)),
                ('paid', models.BooleanField(default=False)),
                ('gas_dealer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.gas_dealer')),
                ('payment_for', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.cylinder_price')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
