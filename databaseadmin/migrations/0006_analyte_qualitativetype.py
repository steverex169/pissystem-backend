# Generated by Django 4.2.13 on 2024-07-19 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0005_alter_analyte_analytetype'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyte',
            name='qualitativetype',
            field=models.CharField(blank=True, choices=[('Positive', 'Positive'), ('Negative', 'Negative'), ('Equivocal', 'Equivocal')], default='Positive', max_length=50),
        ),
    ]
