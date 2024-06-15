# Generated by Django 3.2 on 2024-06-12 05:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '0001_initial'),
        ('staff', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('labowner', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='done_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staff.staff', verbose_name='Approved/Unapproved by'),
        ),
        migrations.AddField(
            model_name='lab',
            name='marketer_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='staff.marketer', verbose_name='Marketer'),
        ),
        migrations.AddField(
            model_name='lab',
            name='organization_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization'),
        ),
        migrations.AddField(
            model_name='activitylog',
            name='offered_test_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.offeredtest', verbose_name='Lab'),
        ),
        migrations.AddField(
            model_name='activitylog',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Lab name'),
        ),
    ]
