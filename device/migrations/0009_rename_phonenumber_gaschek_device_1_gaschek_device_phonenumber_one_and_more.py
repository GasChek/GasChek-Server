# Generated by Django 5.0.2 on 2024-02-19 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("device", "0008_alter_gaschek_device_device_update_time"),
    ]

    operations = [
        migrations.RenameField(
            model_name="gaschek_device",
            old_name="phonenumber_gaschek_device_1",
            new_name="phonenumber_one",
        ),
        migrations.RenameField(
            model_name="gaschek_device",
            old_name="phonenumber_gaschek_device_3",
            new_name="phonenumber_three",
        ),
        migrations.RenameField(
            model_name="gaschek_device",
            old_name="phonenumber_gaschek_device_2",
            new_name="phonenumber_two",
        ),
    ]
