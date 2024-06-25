
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(default='blank', upload_to='organization', verbose_name="Organization's Photo")),
                ('name', models.CharField(max_length=255, null=True)),
                ('user_name', models.CharField(max_length=255, null=True, verbose_name='user name')),
                ('email', models.EmailField(max_length=255, null=True)),
                ('phone', models.CharField(help_text='Please use the format: +923123456789', max_length=255, null=True, verbose_name='Contact Number')),
                ('city', models.CharField(max_length=255, null=True)),
                ('country', models.CharField(max_length=255, null=True)),
                ('address', models.CharField(max_length=255, null=True)),
                ('registered_at', models.DateTimeField(max_length=255, null=True)),
                ('account_id', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
