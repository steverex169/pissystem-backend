# Generated by Django 4.2.13 on 2024-07-10 07:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0007_activitylogunits_cycle_cycle_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitylogunits',
            name='cycle',
        ),
        migrations.RemoveField(
            model_name='activitylogunits',
            name='cycle_id',
        ),
        migrations.DeleteModel(
            name='Cycle',
        ),
    ]
