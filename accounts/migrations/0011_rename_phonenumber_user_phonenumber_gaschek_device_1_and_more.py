# Generated by Django 4.1.5 on 2023-02-06 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_gaschek_device_alarm_alter_gaschek_device_call_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='phonenumber',
            new_name='phonenumber_gaschek_device_1',
        ),
        migrations.AddField(
            model_name='user',
            name='phonenumber_gaschek_device_2',
            field=models.CharField(blank=True, max_length=25),
        ),
        migrations.AddField(
            model_name='user',
            name='phonenumber_gaschek_device_3',
            field=models.CharField(blank=True, max_length=25),
        ),
        migrations.AddField(
            model_name='user',
            name='phonenumber_ordering',
            field=models.CharField(blank=True, max_length=25),
        ),
    ]
