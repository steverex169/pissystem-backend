# Generated by Django 5.0.7 on 2024-09-18 12:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0006_alter_scheme_analytetype'),
    ]

    operations = [
        migrations.AddField(
            model_name='sample',
            name='Cycle_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.cycle'),
        ),
    ]
