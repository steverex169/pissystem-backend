# Generated by Django 5.0.7 on 2024-09-09 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labowner', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lab',
            name='membership_status',
            field=models.CharField(choices=[('Active', 'Active'), ('Suspended', 'Suspended'), ('Org Suspended', 'Org Suspended')], default='Suspended', max_length=50),
        ),
    ]
