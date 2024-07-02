# Generated by Django 4.2.13 on 2024-06-25 22:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('financeofficer', '0001_initial'),
        ('accountstatement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='donoraccountstatement',
            name='payment_in_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='financeofficer.paymentin', verbose_name='Payment In'),
        ),
    ]
