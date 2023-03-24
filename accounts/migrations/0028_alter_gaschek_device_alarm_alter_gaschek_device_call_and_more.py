# Generated by Django 4.1.5 on 2023-03-22 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_user_is_connected_with_device_and_more'),
    ]

    operations = [
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