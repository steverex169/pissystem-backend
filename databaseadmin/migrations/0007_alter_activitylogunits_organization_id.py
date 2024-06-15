# Generated by Django 3.2 on 2024-06-14 09:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
        ('databaseadmin', '0006_scheme_analytes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitylogunits',
            name='organization_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='databaseadmin_activity_log_units', to='organization.organization'),
        ),
    ]
