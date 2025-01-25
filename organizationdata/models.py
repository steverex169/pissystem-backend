from django.db import models
from account.models import UserAccount
# Create your models here.

PARTNERS = (
    ('XAOS', 'XAOS'),
    ('BETWAR', 'BETWAR'),
)

STATUS = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Block', 'Block'),
    ('Suspend', 'Suspend'),
)
PAYMENTSTATUS = (
    ('Unpaid', 'Unpaid'),
    ('Paid', 'Paid'),
)
COUNTRY = (
    ('France', 'France'),
    ('London, UK', 'London, UK'),
)
BOOKIE = (
    ('Paradise', 'Paradise'),
    ('Betwar', 'Betwar'),
)
ENVIRONMENT = (
    ('Prod', 'Prod'),
    ('Dev', 'Dev'),
)
ACCOUNTPOLICY = (
    ('BM Morning', 'BM Morning'),
    ('BM Evening', 'BM Evening'),
)
CURRENCY_TYPE = (
    ('Afghani', 'Afghani'),
    ('Euro','Euro'),
    ('Dollar', 'Dollar'),
    ('Pakistani Rupees', 'Pakistani Rupees'),
    ('India Rupees', 'India Rupees'),
    ('Pound', 'Pound'),
    ('Dinar', 'Dinar'),
    ('Dirham', 'Dirham'),
    ('Japanese', 'Japanese'),
)

class Organization(models.Model):
    account_id = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True)
    email = models.EmailField(max_length=255, blank=False, null=True)
    country = models.CharField(
        max_length=50, choices=COUNTRY, blank=True, null=True)
    currency = models.CharField(
        max_length=50, choices=CURRENCY_TYPE, blank=True, null=True)
    positiontaking = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bookie = models.CharField(
        max_length=50, choices=BOOKIE, blank=True, null=True)
    environment = models.CharField(
        max_length=50, choices=ENVIRONMENT, blank=True, null=True)
    accountpolicy = models.CharField(
        max_length=50, choices=ACCOUNTPOLICY, blank=True, null=True)

    def __str__(self):
        return self.email

class Scrapdata(models.Model):
    # account_id = models.OneToOneField(
    #     UserAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True)
    partner = models.CharField(
        max_length=50, choices=PARTNERS, blank=True, null=True, default='XAOS')
    partner_name = models.CharField(max_length=1000, blank=True, null=False)
    total = models.CharField(max_length=1000, blank=True, null=False)
    partner_profit = models.CharField(max_length=1000, blank=True, null=False)
    office_profit = models.CharField(max_length=1000, blank=True, null=False)
    website_url = models.CharField(max_length=1000, blank=True, null=False)
    username = models.CharField(max_length=1000, blank=True, null=False)
    password = models.CharField(max_length=1000, blank=True, null=False)
    figure = models.CharField(max_length=1000, blank=True, null=False)
    affiliate_profit = models.CharField(max_length=1000, blank=True, null=False)
    office_profit_dropdown = models.CharField(max_length=1000, blank=True, null=False)
    weekly = models.CharField(max_length=1000, blank=True, null=False)

    def __str__(self):
        return self.partner or "No Partner"
