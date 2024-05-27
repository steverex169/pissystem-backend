from datetime import datetime
from django.contrib.gis.db import models

from account.models import UserAccount

# Create your models here.
OPTIONS = (
    ('b2b-admin', 'B2B Admin'),
    ('database-admin', 'Database Admin'),
    ('csr-admin', 'CSR Admin'),
    ('hr-admin', 'HR Admin'),
    ('finance-admin', 'Finance Admin'),
    ('auditor-admin', 'Auditor Admin'),
    ('registration-admin', 'Registration Admin'),
    ('database-admin', 'Database Admin'),
    ('CSR', 'CSR'),
    ('auditor', 'Auditor'),
    ('finance-officer', 'Finance Officer'),
    ('marketer-admin', 'Marketer Admin')
)

TERRITORY_OFFICES = (
    ('Central Office', 'Central Office'),
    ('North Office', 'North Office'),
    ('South Office', 'South Office'),
)

class Staff(models.Model):
    photo = models.ImageField(
        upload_to='staff', verbose_name='Staff\'s Photo', default="blank")
    account_id = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    user_name = models.CharField(max_length=255, blank=False,
                            null=True, verbose_name='user name')
    cnic = models.CharField(max_length=255, blank=False, null=True,
                            verbose_name='CNIC Number', help_text='Please add backslashes as well.')
    email = models.EmailField(max_length=255, blank=False, null=True)
    phone = models.CharField(max_length=255, blank=False, null=True,
                             verbose_name='Contact Number', help_text="Please use the format: +923123456789")
    staff_type = models.CharField(
        max_length=100, choices=OPTIONS, blank=True, null=True)
    city = models.CharField(max_length=255, blank=False, null=True)
    registered_at = models.DateTimeField(
        max_length=255, null=True, blank=False)

    def __str__(self):
        return self.name


class Marketer(models.Model):
    name = models.CharField(max_length=255, blank=False, null=True)
    cnic = models.CharField(max_length=255, unique=True, blank=False, null=True,
                            verbose_name='CNIC Number', help_text='Please add backslashes as well.')
    email = models.EmailField(
        max_length=255, unique=True, blank=False, null=True)
    phone = models.CharField(max_length=255, blank=False, null=True,
                             verbose_name='Contact Number', help_text="Please use the format: +923123456789")
    city = models.CharField(max_length=255, blank=False, null=True)
    count = models.PositiveIntegerField(
        blank=False, null=True, verbose_name='Count of Registered Labs', default=1)
    total_count = models.PositiveIntegerField(
        blank=False, null=True, verbose_name='Count of Total Registered Labs', default=1)
    registered_at = models.DateTimeField(
        null=True, blank=False)
    last_paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name

