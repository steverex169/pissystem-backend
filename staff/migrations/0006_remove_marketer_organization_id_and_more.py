# Generated by Django 4.2.13 on 2024-06-10 08:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0005_marketer_organization_id_staff_organization_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='marketer',
            name='organization_id',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='organization_id',
        ),
    ]
