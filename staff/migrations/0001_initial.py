# Generated by Django 3.2 on 2024-09-09 05:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizationdata', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(default='blank', upload_to='staff', verbose_name="Staff's Photo")),
                ('name', models.CharField(max_length=255, null=True)),
                ('user_name', models.CharField(max_length=255, null=True, verbose_name='user name')),
                ('cnic', models.CharField(help_text='Please add backslashes as well.', max_length=255, null=True, verbose_name='CNIC Number')),
                ('email', models.EmailField(max_length=255, null=True)),
                ('phone', models.CharField(help_text='Please use the format: +923123456789', max_length=255, null=True, verbose_name='Contact Number')),
                ('staff_type', models.CharField(blank=True, choices=[('b2b-admin', 'B2B Admin'), ('database-admin', 'Database Admin'), ('csr-admin', 'CSR Admin'), ('hr-admin', 'HR Admin'), ('finance-admin', 'Finance Admin'), ('auditor-admin', 'Auditor Admin'), ('registration-admin', 'Registration Admin'), ('database-admin', 'Database Admin'), ('CSR', 'CSR'), ('auditor', 'Auditor'), ('finance-officer', 'Finance Officer'), ('marketer-admin', 'Marketer Admin'), ('superadmin', 'Superadmin')], max_length=100, null=True)),
                ('city', models.CharField(max_length=255, null=True)),
                ('registered_at', models.DateTimeField(max_length=255, null=True)),
                ('status', models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], default='Active', max_length=50)),
                ('account_id', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organizationdata.organization')),
            ],
        ),
        migrations.CreateModel(
            name='Marketer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True)),
                ('cnic', models.CharField(help_text='Please add backslashes as well.', max_length=255, null=True, unique=True, verbose_name='CNIC Number')),
                ('email', models.EmailField(max_length=255, null=True, unique=True)),
                ('phone', models.CharField(help_text='Please use the format: +923123456789', max_length=255, null=True, verbose_name='Contact Number')),
                ('city', models.CharField(max_length=255, null=True)),
                ('count', models.PositiveIntegerField(default=1, null=True, verbose_name='Count of Registered Labs')),
                ('total_count', models.PositiveIntegerField(default=1, null=True, verbose_name='Count of Total Registered Labs')),
                ('registered_at', models.DateTimeField(null=True)),
                ('last_paid_at', models.DateTimeField(blank=True, null=True)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organizationdata.organization')),
            ],
        ),
    ]
