# Generated by Django 5.0.7 on 2025-01-28 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizationdata', '0009_scrapdata_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='scrapdata',
            name='partner_percentage',
            field=models.CharField(blank=True, default=0, max_length=1000),
        ),
    ]
