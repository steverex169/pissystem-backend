# Generated by Django 4.2.13 on 2024-07-10 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('databaseadmin', '0002_activitylogunits_added_by_sample_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cycle',
            name='analytes',
        ),
        migrations.AddField(
            model_name='scheme',
            name='analytes',
            field=models.ManyToManyField(blank=True, to='databaseadmin.analyte'),
        ),
        migrations.AddField(
            model_name='scheme',
            name='price',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='activitylogunits',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='activitylogunits',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cycle',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='cycle',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
