# Generated by Django 3.2 on 2024-07-13 11:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registrationadmin', '0006_auto_20240713_1541'),
    ]

    operations = [
        migrations.RenameField(
            model_name='selectedscheme',
            old_name='participant_id',
            new_name='participant',
        ),
    ]
