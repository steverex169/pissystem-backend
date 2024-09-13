# Generated by Django 5.0.7 on 2024-09-12 07:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0002_alter_cycle_cycle'),
        ('registrationadmin', '0005_selectedscheme_cycle_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='scheme',
        ),
        migrations.AddField(
            model_name='payment',
            name='cycle_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.cycle'),
        ),
    ]
