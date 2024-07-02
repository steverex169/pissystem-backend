# Generated by Django 3.2 on 2024-07-02 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0005_auto_20240702_1303'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activitylogunits',
            name='type_id',
        ),
        migrations.AlterField(
            model_name='activitylogunits',
            name='type',
            field=models.CharField(choices=[('Units', 'Units'), ('Instruments', 'Instruments'), ('Reagent', 'Reagent'), ('Method', 'Method'), ('Manufactural', 'Manufactural'), ('Analyte', 'Analyte'), ('Instrumentlist', 'Instrumentlist'), ('City', 'City'), ('District', 'District'), ('Department', 'Department'), ('Designation', 'Designation'), ('ParticipantSector', 'ParticipantSector')], default='Units', max_length=50, verbose_name='Form type?'),
        ),
        migrations.DeleteModel(
            name='ParticipantType',
        ),
    ]
