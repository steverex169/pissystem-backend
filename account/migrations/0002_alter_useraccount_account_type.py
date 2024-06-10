# Generated by Django 4.1.3 on 2024-06-08 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='account_type',
            field=models.CharField(blank=True, choices=[('admin', 'Admin'), ('database-admin', 'Database Admin'), ('hr-admin', 'HR Admin'), ('CSR', 'CSR'), ('registration-admin', 'Registration Admin'), ('labowner', 'Lab'), ('finance-officer', 'Finance Officer'), ('organization', 'Organization')], default='admin', max_length=100),
        ),
    ]
