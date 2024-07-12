# Generated by Django 4.2.13 on 2024-07-11 10:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('databaseadmin', '0001_initial'),
        ('labowner', '__first__'),
        ('organization', '0001_initial'),
        ('registrationadmin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveBigIntegerField(null=True)),
                ('discount', models.PositiveBigIntegerField(null=True)),
                ('photo', models.CharField(max_length=255, null=True)),
                ('paymentmethod', models.CharField(blank=True, null=True)),
                ('paydate', models.DateField(blank=True, null=True)),
                ('account_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
                ('participant_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab')),
                ('scheme', models.ManyToManyField(blank=True, to='databaseadmin.scheme')),
            ],
            options={
                'verbose_name': 'Payment',
            },
        ),
    ]
