# Generated by Django 3.2 on 2024-06-13 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labowner', '0002_auto_20240612_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='email_participant',
            field=models.EmailField(max_length=70, null=True),
        ),
    ]
