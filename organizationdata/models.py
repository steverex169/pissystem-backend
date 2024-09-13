from django.db import models
from account.models import UserAccount
# Create your models here.

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
    name = models.CharField(max_length=255, blank=False, null=True)
    user_name = models.CharField(max_length=255, blank=False,
                            null=True, verbose_name='user name')
    email = models.EmailField(max_length=255, blank=False, null=True)
    country = models.CharField(max_length=255, blank=False, null=True)
    website = models.CharField(max_length=255, blank=False, null=True)
    registered_at = models.DateTimeField(
        max_length=255, null=True, blank=False)
    photo = models.ImageField(
        upload_to='organization', verbose_name='Organization\'s Photo', default="blank")
    status = models.CharField(
        max_length=50, choices=STATUS, default='Pending')
    payment_status = models.CharField(
        max_length=50, choices=PAYMENTSTATUS, default='Unpaid')
    currency = models.CharField(
        max_length=50, choices=CURRENCY_TYPE, blank=True, null=True)
    payment_proof = models.ImageField(
        upload_to='organization', verbose_name='Organization\'s Photo', default="blank")
    issue_date = models.DateTimeField(blank=True, null=True)
    closing_date = models.DateTimeField(blank=True, null=True)
    amount = models.CharField(max_length=255,blank=False, null=True)

    def __str__(self):
        return self.name

        