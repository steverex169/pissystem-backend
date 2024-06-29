# Generated by Django 4.2.13 on 2024-06-25 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0004_remove_analyte_reagent_analyte_reagents'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analyte',
            name='instrument',
        ),
        migrations.RemoveField(
            model_name='analyte',
            name='method',
        ),
        migrations.RemoveField(
            model_name='analyte',
            name='unit',
        ),
        migrations.AddField(
            model_name='analyte',
            name='instruments',
            field=models.ManyToManyField(blank=True, to='databaseadmin.instrument'),
        ),
        migrations.AddField(
            model_name='analyte',
            name='methods',
            field=models.ManyToManyField(blank=True, to='databaseadmin.method'),
        ),
        migrations.AddField(
            model_name='analyte',
            name='units',
            field=models.ManyToManyField(blank=True, to='databaseadmin.units'),
        ),
    ]
