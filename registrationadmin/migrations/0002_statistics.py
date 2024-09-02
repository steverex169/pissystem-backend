# Generated by Django 3.2 on 2024-08-30 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0001_initial'),
        ('organization', '__first__'),
        ('labowner', '__first__'),
        ('registrationadmin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lab_count', models.PositiveBigIntegerField(blank=True, null=True)),
                ('mean_result', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('median_result', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('robust_mean', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('std_deviation', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('uncertainty', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('cv_percentage', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('z_scores_with_lab', models.JSONField(blank=True, default=list, null=True)),
                ('result', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('rounds', models.PositiveBigIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('analyte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.analyte')),
                ('organization_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
                ('participant_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='labowner.lab')),
                ('scheme', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='databaseadmin.scheme')),
            ],
            options={
                'verbose_name': 'Statistics',
            },
        ),
    ]
