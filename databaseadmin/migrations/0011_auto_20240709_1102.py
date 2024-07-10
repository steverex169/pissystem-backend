# Generated by Django 3.2 on 2024-07-09 06:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0002_organization_website'),
        ('databaseadmin', '0010_auto_20240704_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitylogunits',
            name='type',
            field=models.CharField(choices=[('Units', 'Units'), ('Instruments', 'Instruments'), ('Reagent', 'Reagent'), ('Method', 'Method'), ('Manufactural', 'Manufactural'), ('Analyte', 'Analyte'), ('City', 'City'), ('ParticipantCountry', 'ParticipantCountry'), ('ParticipantProvince', 'ParticipantProvince'), ('District', 'District'), ('Department', 'Department'), ('Designation', 'Designation'), ('ParticipantType', 'ParticipantType'), ('ParticipantSector', 'ParticipantSector')], default='Units', max_length=50, verbose_name='Form type?'),
        ),
        migrations.CreateModel(
            name='ParticipantProvince',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Participant Province',
            },
        ),
        migrations.CreateModel(
            name='ParticipantCountry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Participant Country',
            },
        ),
    ]
