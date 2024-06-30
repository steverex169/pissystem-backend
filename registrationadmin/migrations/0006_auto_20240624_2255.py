# Generated by Django 3.2 on 2024-06-25 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrationadmin', '0005_round_cycle_no'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='round',
            name='status',
        ),
        migrations.AddField(
            model_name='round',
            name='Option',
            field=models.CharField(blank=True, choices=[('Created', 'Created'), ('Ready', 'Ready'), ('Issued', 'Issued'), ('Open', 'Open'), ('Saved', 'Saved'), ('Submitted', 'Submitted'), ('Closed', 'Closed'), ('Report Available', 'Report Available')], default='Created', max_length=50),
        ),
    ]
