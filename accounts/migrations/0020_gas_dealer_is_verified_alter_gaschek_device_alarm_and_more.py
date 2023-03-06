# Generated by Django 4.1.5 on 2023-03-06 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0019_abandoned_subaccounts'),
    ]

    operations = [
        migrations.AddField(
            model_name='gas_dealer',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gaschek_device',
            name='alarm',
            field=models.CharField(choices=[('off', 'off'), ('on', 'on')], default='off', max_length=10),
        ),
        migrations.AlterField(
            model_name='gaschek_device',
            name='call',
            field=models.CharField(choices=[('off', 'off'), ('on', 'on')], default='off', max_length=10),
        ),
        migrations.AlterField(
            model_name='gaschek_device',
            name='text',
            field=models.CharField(choices=[('off', 'off'), ('on', 'on')], default='off', max_length=10),
        ),
    ]
