# Generated by Django 4.2.13 on 2024-07-11 10:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analyte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('code', models.PositiveBigIntegerField(blank=True, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Inactive', max_length=50)),
            ],
            options={
                'verbose_name': 'Analyte',
            },
        ),
        migrations.CreateModel(
            name='Manufactural',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('website', models.CharField(max_length=10000000, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Database Manufactural',
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
        migrations.CreateModel(
            name='Units',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Database Unit',
            },
        ),
        migrations.CreateModel(
            name='Scheme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Scheme')),
                ('price', models.CharField(blank=True, max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Inactive', max_length=50)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('analytes', models.ManyToManyField(blank=True, to='databaseadmin.analyte')),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Scheme',
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sampleno', models.CharField(max_length=255, null=True)),
                ('details', models.TextField()),
                ('notes', models.TextField(max_length=255, null=True)),
                ('scheme', models.TextField(blank=True, null=True)),
                ('account_id', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Sample',
            },
        ),
        migrations.CreateModel(
            name='Reagents',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('code', models.PositiveBigIntegerField(null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Inactive', max_length=50)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='databaseadmin.participantcountry')),
                ('manufactural', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='databaseadmin.manufactural')),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Database Reagent',
            },
        ),
        migrations.CreateModel(
            name='ParticipantType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Participant Type',
            },
        ),
        migrations.CreateModel(
            name='ParticipantSector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Participant Sector',
            },
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
            name='News',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, null=True)),
                ('description', models.TextField()),
                ('picture', models.ImageField(blank=True, null=True, upload_to='news_pictures/')),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'News',
            },
        ),
        migrations.CreateModel(
            name='Method',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('code', models.PositiveBigIntegerField(blank=True, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Inactive', max_length=50)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Method',
            },
        ),
        migrations.AddField(
            model_name='manufactural',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='databaseadmin.participantcountry'),
        ),
        migrations.AddField(
            model_name='manufactural',
            name='organization_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization'),
        ),
        migrations.CreateModel(
            name='InstrumentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Instrument type')),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Instrument type',
            },
        ),
        migrations.CreateModel(
            name='Instrument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Instrument')),
                ('code', models.PositiveBigIntegerField(null=True)),
                ('model', models.CharField(max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Inactive', max_length=50)),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='databaseadmin.participantcountry')),
                ('instrument_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='databaseadmin.instrumenttype')),
                ('manufactural', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='databaseadmin.manufactural')),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Instrument',
            },
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Participant District',
            },
        ),
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Participant Designation',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Participant Department',
            },
        ),
        migrations.CreateModel(
            name='Cycle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cycle_no', models.CharField(blank=True, max_length=255, null=True)),
                ('rounds', models.PositiveBigIntegerField(blank=True, null=True)),
                ('cycle', models.CharField(blank=True, choices=[('Months', 'Months'), ('Year', 'Year')], default='Months', max_length=50)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Inactive', max_length=50)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
                ('scheme_name', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.scheme')),
            ],
            options={
                'verbose_name': 'Cycle',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
            ],
            options={
                'verbose_name': 'Participant City',
            },
        ),
        migrations.AddField(
            model_name='analyte',
            name='instruments',
            field=models.ManyToManyField(blank=True, to='databaseadmin.instrument'),
        ),
        migrations.AddField(
            model_name='analyte',
            name='master_unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='master_unit', to='databaseadmin.units'),
        ),
        migrations.AddField(
            model_name='analyte',
            name='methods',
            field=models.ManyToManyField(blank=True, to='databaseadmin.method'),
        ),
        migrations.AddField(
            model_name='analyte',
            name='organization_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization'),
        ),
        migrations.AddField(
            model_name='analyte',
            name='reagents',
            field=models.ManyToManyField(blank=True, to='databaseadmin.reagents'),
        ),
        migrations.AddField(
            model_name='analyte',
            name='units',
            field=models.ManyToManyField(blank=True, to='databaseadmin.units'),
        ),
        migrations.CreateModel(
            name='ActivityLogUnits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_value', models.TextField(blank=True, null=True)),
                ('new_value', models.TextField(blank=True, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('date_of_updation', models.DateTimeField(auto_now=True, null=True)),
                ('field_name', models.CharField(max_length=255, null=True)),
                ('actions', models.CharField(choices=[('Updated', 'Updated'), ('Added', 'Added'), ('Deleted', 'Deleted')], default='Added', max_length=50, verbose_name='Which action is performed?')),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Inactive', max_length=50)),
                ('type', models.CharField(choices=[('Units', 'Units'), ('Instruments', 'Instruments'), ('Reagent', 'Reagent'), ('Method', 'Method'), ('Manufactural', 'Manufactural'), ('Analyte', 'Analyte'), ('Instrumentlist', 'Instrumentlist'), ('City', 'City'), ('ParticipantCountry', 'ParticipantCountry'), ('ParticipantProvince', 'ParticipantProvince'), ('District', 'District'), ('Department', 'Department'), ('Designation', 'Designation'), ('ParticipantType', 'ParticipantType'), ('ParticipantSector', 'ParticipantSector')], default='Units', max_length=50, verbose_name='Form type?')),
                ('analyte_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.analyte')),
                ('city_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.city')),
                ('country_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.participantcountry')),
                ('cycle_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.cycle')),
                ('department_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.department')),
                ('designation_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.designation')),
                ('district_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.district')),
                ('instrument_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.instrument')),
                ('instrumenttype_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.instrumenttype')),
                ('manufactural_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.manufactural')),
                ('method_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.method')),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='databaseadmin_activity_log_units', to='organization.organization')),
                ('province_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.participantprovince')),
                ('reagent_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.reagents')),
                ('sample_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.sample')),
                ('scheme_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.scheme')),
                ('sector_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.participantsector')),
                ('type_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.participanttype')),
                ('unit_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.units')),
            ],
            options={
                'verbose_name': 'History',
            },
        ),
    ]
