# Generated by Django 4.1.5 on 2023-01-31 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_email_alter_user_usernames'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(
                blank=True, default=None, max_length=50, null=True, unique=True),
        ),
    ]
