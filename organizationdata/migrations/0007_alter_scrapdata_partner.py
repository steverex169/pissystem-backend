# Generated by Django 5.0.7 on 2025-01-22 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizationdata', '0006_scrapdata_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scrapdata',
            name='partner',
            field=models.CharField(blank=True, choices=[('XAOS', 'XAOS'), ('BETWAR', 'BETWAR')], default='XAOS', max_length=50, null=True),
        ),
    ]
