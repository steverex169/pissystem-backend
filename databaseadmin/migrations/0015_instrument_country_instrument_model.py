# Generated by Django 4.2.13 on 2024-07-05 06:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0014_alter_activitylogunits_type_participantcountry_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='instrument',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='databaseadmin.participantcountry'),
        ),
        migrations.AddField(
            model_name='instrument',
            name='model',
            field=models.CharField(null=True),
        ),
    ]
