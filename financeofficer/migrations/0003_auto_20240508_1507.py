# Generated by Django 3.2 on 2024-05-08 10:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financeofficer', '0002_auto_20240508_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentin',
            name='lab_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab', verbose_name='Lab'),
        ),
        migrations.AddField(
            model_name='paymentout',
            name='lab_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab', verbose_name='Lab'),
        ),
    ]
