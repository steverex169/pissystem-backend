# Generated by Django 3.2 on 2024-09-09 05:25

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('staff', '0001_initial'),
        ('databaseadmin', '0001_initial'),
        ('organizationdata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lab',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='Lab name')),
                ('user_name', models.CharField(max_length=255, null=True, verbose_name='user name')),
                ('financial_settlement', models.CharField(blank=True, choices=[('Self', 'Self'), ('Main Lab', 'Main Lab')], default='Self', max_length=50, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logo', verbose_name='Logo')),
                ('lab_experience', models.PositiveIntegerField(blank=True, null=True, verbose_name='Lab Experience (Years)')),
                ('email', models.EmailField(max_length=70, null=True)),
                ('email_participant', models.EmailField(max_length=70, null=True)),
                ('phone', models.CharField(blank=True, help_text='Please use the format: +923123456789', max_length=255, null=True, verbose_name='Phone')),
                ('landline', models.CharField(help_text='Please use the format: +922134552799', max_length=20, null=True)),
                ('fax', models.CharField(help_text='Please use the format: + (Country Code) (City Code without the leading zero) (fax number)', max_length=20, null=True)),
                ('address', models.CharField(help_text='Please enter your address to automatically locate it on map.', max_length=255, null=True, verbose_name='Address')),
                ('billing_address', models.CharField(blank=True, max_length=255, null=True)),
                ('shipping_address', models.CharField(blank=True, max_length=255, null=True)),
                ('department', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('province', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('state', models.CharField(blank=True, max_length=255, null=True)),
                ('registered_at', models.DateTimeField(null=True)),
                ('registered_by', models.CharField(choices=[('Lab', 'Lab'), ('Marketer', 'Marketer')], default='Lab', max_length=50)),
                ('lab_staff_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Registered by (Name)')),
                ('lab_staff_designation', models.CharField(blank=True, max_length=255, null=True, verbose_name='Designation')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Accept', 'Accept'), ('Unapproved', 'Unapproved'), ('Cencel Request', 'Cencel Request'), ('Cencel', 'Cencel')], default='Pending', max_length=50)),
                ('done_at', models.DateTimeField(blank=True, max_length=255, null=True, verbose_name='Approved/Unapproved at')),
                ('postalcode', models.CharField(blank=True, max_length=255, null=True)),
                ('organization', models.CharField(blank=True, max_length=255, null=True, verbose_name='organization name')),
                ('is_active', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='Yes', max_length=50, null=True, verbose_name='Is lab active for the services?')),
                ('is_blocked', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='No', max_length=50, null=True, verbose_name='Is lab blocked from using our services?')),
                ('is_temporary_blocked', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='No', max_length=50, null=True, verbose_name='Is lab temporary blocked from using our services?')),
                ('is_approved', models.BooleanField(default=0, null=True)),
                ('website', models.URLField(blank=True, null=True, verbose_name='Website')),
                ('district', models.CharField(blank=True, max_length=255, null=True)),
                ('landline_registered_by', models.CharField(help_text='Please use the format: +922134552799', max_length=30, null=True)),
                ('payment_status', models.CharField(choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid', max_length=50)),
                ('membership_status', models.CharField(choices=[('Active', 'Active'), ('Suspended', 'Suspended')], default='Suspended', max_length=50)),
                ('account_id', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('marketer_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staff.marketer', verbose_name='Marketer')),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organizationdata.organization')),
                ('staff_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staff.staff')),
            ],
            options={
                'verbose_name': 'Lab',
            },
        ),
        migrations.CreateModel(
            name='SampleCollector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female')], default='Male', max_length=50, null=True)),
                ('cnic', models.CharField(help_text='Please use the format XXXXX-XXXXXXX-X', max_length=255, null=True, verbose_name='CNIC')),
                ('photo', models.ImageField(upload_to='samplecollectors', verbose_name="Sample Collector's Photo")),
                ('phone', models.CharField(help_text='Please use the format: +923123456789', max_length=255, null=True)),
                ('account_id', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('lab_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab', verbose_name='Lab name')),
            ],
            options={
                'verbose_name': 'Home Sample Collector',
            },
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheme_id', models.CharField(blank=True, max_length=255, null=True)),
                ('result', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('result_status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Accept', 'Accept'), ('Unapproved', 'Unapproved'), ('Cencel Request', 'Cencel Request'), ('Submited', 'Submited')], default='Pending', max_length=50)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
                ('rounds', models.PositiveBigIntegerField(blank=True, null=True)),
                ('analyte', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.analyte', verbose_name='Analyte')),
                ('instrument', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.instrument', verbose_name='Instrument')),
                ('lab_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab', verbose_name='Lab')),
                ('method', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.method', verbose_name='Method')),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organizationdata.organization')),
                ('reagents', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.reagents', verbose_name='Reagents')),
                ('units', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.units', verbose_name='Units')),
            ],
            options={
                'verbose_name': 'Result',
            },
        ),
        migrations.CreateModel(
            name='Pathologist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('email', models.EmailField(max_length=255, null=True)),
                ('phone', models.CharField(help_text='Please use the format: +923123456789', max_length=255, null=True, verbose_name='Phone')),
                ('landline', models.CharField(blank=True, help_text='Please use the format: +922134552799', max_length=13, null=True)),
                ('photo', models.ImageField(null=True, upload_to='pathologist', verbose_name='Photo')),
                ('pmdc_reg_no', models.CharField(max_length=255, null=True)),
                ('qualification', models.CharField(blank=True, max_length=255, null=True)),
                ('speciality', models.CharField(blank=True, max_length=255, null=True)),
                ('designation', models.CharField(blank=True, max_length=255, null=True)),
                ('is_available_for_consultation', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='Yes', max_length=50, verbose_name='Is available for online consultation?')),
                ('is_available_on_whatsapp', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='Yes', max_length=50, verbose_name='Are you available on WhatsApp?')),
                ('is_associated_with_pap', models.CharField(blank=True, choices=[('Yes', 'Yes'), ('No', 'No')], max_length=50, null=True, verbose_name='Are you associated with PAP?')),
                ('lab_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab', verbose_name='Lab name')),
            ],
            options={
                'verbose_name': 'Pathologist',
            },
        ),
        migrations.CreateModel(
            name='LabPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_id', models.CharField(max_length=5, null=True, unique=True)),
                ('payment_method', models.CharField(choices=[('Cash', 'Cash'), ('Cheque', 'Cheque'), ('Card', 'Card')], default='Cash', max_length=50)),
                ('address_type', models.CharField(blank=True, choices=[('Pick from', 'Pick from'), ('Deliever to', 'Deliever to')], max_length=50, null=True)),
                ('address', models.CharField(blank=True, max_length=255, null=True)),
                ('amount', models.PositiveBigIntegerField(null=True)),
                ('paid_at', models.DateTimeField(blank=True, max_length=255, null=True)),
                ('cheque_no', models.CharField(blank=True, max_length=255, null=True)),
                ('cheque_image', models.ImageField(blank=True, null=True, upload_to='cheque', verbose_name='Cheque Image')),
                ('deposited_at', models.DateTimeField(blank=True, max_length=255, null=True)),
                ('deposit_slip', models.ImageField(blank=True, null=True, upload_to='deposit_slip', verbose_name='Deposit Slip')),
                ('is_cleared', models.BooleanField(blank=True, default=0, null=True)),
                ('cleared_at', models.DateTimeField(blank=True, max_length=255, null=True)),
                ('is_settled', models.BooleanField(blank=True, default=0, null=True)),
                ('settled_at', models.DateTimeField(blank=True, max_length=255, null=True)),
                ('lab_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab', verbose_name='Lab')),
            ],
            options={
                'verbose_name': 'Lab Payment',
            },
        ),
        migrations.CreateModel(
            name='LabCorporate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shared_percentage', models.FloatField(blank=True, default=0.02, null=True, verbose_name='Referral Fee Percentage')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Accept', 'Accept'), ('Unapproved', 'Unapproved'), ('Cencel Request', 'Cencel Request'), ('Cencel', 'Cencel')], default='Pending', max_length=50)),
                ('remaining_amount', models.PositiveIntegerField(default=0, null=True)),
                ('allow_all', models.CharField(choices=[('Yes', 'Yes'), ('No', 'No')], default='No', max_length=50, null=True)),
                ('lab_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab', verbose_name='Lab name')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=255, null=True)),
                ('old_value', models.TextField(null=True)),
                ('new_value', models.TextField(null=True)),
                ('old_discount_by_lab', models.TextField(null=True)),
                ('new_discount_by_lab', models.TextField(null=True)),
                ('start_date_by_lab', models.DateTimeField(blank=True, max_length=255, null=True)),
                ('end_date_by_lab', models.DateTimeField(blank=True, default=datetime.datetime.now, max_length=255, null=True)),
                ('old_discount_by_labhazir', models.TextField(null=True)),
                ('new_discount_by_labhazir', models.TextField(null=True)),
                ('start_date_by_labhazir', models.DateTimeField(blank=True, max_length=255, null=True)),
                ('end_date_by_labhazir', models.DateTimeField(blank=True, default=datetime.datetime.now, max_length=255, null=True)),
                ('actions', models.CharField(choices=[('Updated', 'Updated'), ('Added', 'Added'), ('Deleted', 'Deleted')], default='Updated', max_length=50, verbose_name='Which action is performed?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Lab name')),
            ],
            options={
                'verbose_name': 'Activity Log',
            },
        ),
    ]
