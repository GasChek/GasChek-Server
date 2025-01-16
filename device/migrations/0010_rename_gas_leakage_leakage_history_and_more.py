# Generated by Django 5.0.2 on 2024-02-19 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "device",
            "0009_rename_phonenumber_gaschek_device_1_gaschek_device_phonenumber_one_and_more",
        ),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Gas_Leakage",
            new_name="Leakage_History",
        ),
        migrations.RenameField(
            model_name="leakage_history",
            old_name="gaschek_device",
            new_name="device",
        ),
        migrations.AlterField(
            model_name="gaschek_device",
            name="alarm",
            field=models.CharField(
                choices=[("off", "off"), ("on", "on")], default="off", max_length=10
            ),
        ),
        migrations.AlterField(
            model_name="gaschek_device",
            name="call",
            field=models.CharField(
                choices=[("off", "off"), ("on", "on")], default="off", max_length=10
            ),
        ),
        migrations.AlterField(
            model_name="gaschek_device",
            name="indicator",
            field=models.CharField(
                choices=[("off", "off"), ("on", "on")], default="off", max_length=10
            ),
        ),
        migrations.AlterField(
            model_name="gaschek_device",
            name="text",
            field=models.CharField(
                choices=[("off", "off"), ("on", "on")], default="off", max_length=10
            ),
        ),
    ]
