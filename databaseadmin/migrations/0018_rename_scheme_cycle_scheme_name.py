# Generated by Django 3.2 on 2024-06-30 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0017_rename_scheme_name_cycle_scheme'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cycle',
            old_name='scheme',
            new_name='scheme_name',
        ),
    ]
