# Generated by Django 3.2 on 2024-07-04 11:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0002_organization_website'),
        ('databaseadmin', '0010_auto_20240704_1333'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('labowner', '0003_alter_lab_landline_registered_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rounds', models.PositiveBigIntegerField(blank=True, null=True)),
                ('cycle_no', models.CharField(blank=True, max_length=255, null=True)),
                ('sample', models.CharField(blank=True, max_length=255, null=True)),
                ('issue_date', models.DateTimeField(blank=True, null=True)),
                ('closing_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('Created', 'Created'), ('Ready', 'Ready'), ('Open', 'Open'), ('Closed', 'Closed'), ('Report Available', 'Report Available')], max_length=50)),
                ('account_id', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('labs', models.ManyToManyField(blank=True, to='labowner.Lab')),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
                ('scheme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.scheme')),
            ],
            options={
                'verbose_name': 'Round',
            },
        ),
        migrations.CreateModel(
            name='ActivityLogUnits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue_date', models.DateTimeField(blank=True, null=True)),
                ('closing_date', models.DateTimeField(blank=True, null=True)),
                ('old_value', models.TextField(blank=True, null=True)),
                ('new_value', models.TextField(blank=True, null=True)),
                ('date_of_addition', models.DateTimeField(blank=True, null=True)),
                ('date_of_updation', models.DateTimeField(auto_now=True, null=True)),
                ('field_name', models.CharField(max_length=255, null=True)),
                ('actions', models.CharField(choices=[('Updated', 'Updated'), ('Added', 'Added'), ('Deleted', 'Deleted')], default='Added', max_length=50, verbose_name='Which action is performed?')),
                ('status', models.CharField(blank=True, choices=[('Created', 'Created'), ('Ready', 'Ready'), ('Open', 'Open'), ('Closed', 'Closed'), ('Report Available', 'Report Available')], max_length=50)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registrationadmin_activity_log_units', to='organization.organization')),
                ('round_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='registrationadmin.round')),
            ],
            options={
                'verbose_name': 'History',
            },
        ),
    ]
