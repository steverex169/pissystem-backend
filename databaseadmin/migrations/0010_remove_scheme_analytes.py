# Generated by Django 3.2 on 2024-06-15 07:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0009_scheme_analytes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scheme',
            name='analytes',
        ),
    ]
