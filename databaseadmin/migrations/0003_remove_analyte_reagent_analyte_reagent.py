# Generated by Django 4.2.13 on 2024-06-13 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0002_remove_news_added_by_analyte_allowed_units_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='analyte',
            name='reagent',
        ),
        migrations.AddField(
            model_name='analyte',
            name='reagent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='databaseadmin.reagents'),
        ),
    ]
