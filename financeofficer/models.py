from django.db import models

# Create your models here.

from django.contrib.gis.db import models
from account.models import UserAccount
# from financeadmin.models import BankAccount, Bank
from staff.models import Staff
# from donor.models import Donor
from labowner.models import Lab
# from b2bclient.models import B2BClient
# from marketeradmin.admin import Advertisement
from django.core.validators import RegexValidator 

# from labowner.models import Lab
# Create your models here.

OPTIONS = (
    ('Yes', 'Yes'),
    ('No', 'No')
)

PAYMENT_METHOD = (
    ('Cash', 'Cash'),
    ('Cheque', 'Cheque'),
    ('Card', 'Card'),
)

TRANSFER_TYPE = (
    ('Deposit', 'Deposit'),
    ('Interbank Transfer', 'Interbank Transfer'),
    ('Withdraw', 'Withdraw'),
)
DEPOSIT_TYPE = (
    ('Loan Return', 'Loan Return'),
    ('Asset Sale', 'Asset Sale'),
    ('Insurance Claim', 'Insurance Claim'),
    ('Investments', 'Investments'),
    ('Others', 'Others'),
)
WITHDRAW_TYPE = (
    ('Loan', 'Loan'),
    ('Tax', 'Tax'),
    ('Legal and Professional Expenses', 'Legal and Professional Expenses'),
    ('Investments', 'Investments'),
    ('Utilities', 'Utilities'),
    ('Salary and Wages', 'Salary and Wages'),
    ('Rent', 'Rent'),
    ('Marketing', 'Marketing'),
    ('Insurance and Securities', 'Insurance and Securities'),
    ('Employee Expense', 'Employee Expense'),
    ('Donation and Charity', 'Donation and Charity'),
    ('Delivery Expense', 'Delivery Expense'),
    ('Telecommunication', 'Telecommunication'),
    ('Travel and Tours', 'Travel and Tours'),
    ('Others', 'Others'),
)
MODE = (
    ('Cash', 'Cash'),
    ('Cheque', 'Cheque'),
    ('Online', 'Online'),
    # ('Bank Form', 'Bank Form'),
)


STATUS = (
    ('Created', 'Created'),
    ('Deposited', 'Deposited'),
    ('Cleared', 'Cleared'),
    ('Approved', 'Approved'),
    ('Unapproved', 'Unapproved'),
    ('Pending Clearance', 'Pending Clearance'),
    ('Bounced', 'Bounced')

)
TYPE= (
    ('Payment In', 'Payment In'),
    ('Payment Out', 'Payment Out'),
    ('Invoice Adjustment', 'Invoice Adjustment'),
    # ('Bank Transfer Detail','Bank Transfer Detail')
)
ACTIONS= (
    ('Updated', 'Updated'),
    ('Added', 'Added'),
    ('Deleted', 'Deleted'),
)
PAYMENT_FOR = (
    ('Lab', 'Lab'),
    ('Marketer', 'Marketer'),
    # ('Donor', 'Donor'),
    # ('B2BClient', 'B2BClient'),
    # ('Advertisement', 'Advertisement'),
    ('Corporate Lab', 'Corporate Lab'),

)
PAYMENT_FOR_FINANCE = (
    ('Lab', 'Lab'),
    ('Marketer', 'Marketer'),
    # ('Donor', 'Donor'),
    # ('B2BClient', 'B2BClient'),
    # ('Advertisement', 'Advertisement'),
    ('Deposit', 'Deposit'),
    ('Interbank Transfer', 'Interbank Transfer'),
    ('Withdraw', 'Withdraw'),
    ('Invoice Adjustment', 'Invoice Adjustment'),
)
TRANSECTION_TYPE = (
    ('Donation', 'Donation'),
    ('Other', 'Other'),

)

class PaymentIn(models.Model):
    payment_for = models.CharField(
        max_length=50, choices=PAYMENT_FOR, default='Lab')
    # advertisement_id = models.ForeignKey(
    #     Advertisement, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Advertisement")
    lab_id = models.ForeignKey(
        Lab, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Lab")
    test_appointment_id = models.CharField(max_length=255, blank=False, null=True)
    # donor_id = models.ForeignKey(
    #     Donor, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Donor")
    # invoice_id = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD, default='Cheque')
    amount = models.PositiveBigIntegerField(blank=False, null=True)
    tax = models.PositiveBigIntegerField(blank=True, null=True)
    cheque_no = models.CharField(max_length=255, blank=True, null=True)
    paid_at = models.DateTimeField(max_length=255, null=True, blank=True)
    # cheque_payment_date = models.DateTimeField(max_length=255, null=True, blank=True)
    refered_no = models.CharField(max_length=255, blank=True, null=True)
    cheque_image = models.ImageField(
        upload_to='cheque', verbose_name='Cheque Image', blank=True, null=True)
    deposited_at = models.DateTimeField(max_length=255, null=True, blank=True)
    # bankaccount_id = models.ForeignKey(
    #     BankAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Bank Account")    
    deposit_slip = models.FileField(
        upload_to='deposit_slip', verbose_name='Deposit Slip', blank=True, null=True)
    recieved_by = models.CharField(max_length=255, blank=True, null=True)
    handover_to = models.CharField(max_length=255, blank=True, null=True)    
    verified_by = models.CharField(max_length=255, blank=False, null=True)
    is_approved = models.BooleanField(default=0, blank=True, null=True)
    is_cleared = models.CharField(max_length=50, choices=OPTIONS, blank=True, null=True)
    cleared_at = models.DateTimeField(
        max_length=255, blank=True, null=True, verbose_name="Cleared At")
    payment_status = models.CharField(
        max_length=50, choices=STATUS, default='Created', blank=True)
    

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Payment In'

class PaymentOut(models.Model):
    payment_for = models.CharField(
        max_length=50, choices=PAYMENT_FOR, default='Lab')
    lab_id = models.ForeignKey(
        Lab, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Lab")
    # b2b_id = models.ForeignKey(
    #     B2BClient, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="B2B")
    transection_type = models.CharField(
        max_length=50, choices=TRANSECTION_TYPE, default='Other')
    test_appointment_id = models.CharField(max_length=255, blank=False, null=True)
    invoice_id = models.CharField(
        max_length=5, unique=True, null=True, blank=False)
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD, default='Cheque')
    amount = models.IntegerField(blank=False, null=True)
    payment_at = models.DateTimeField(max_length=255, null=True, blank=True)
    cheque_no = models.CharField(max_length=255, blank=True, null=True)
    # bankaccount_id = models.ForeignKey(
    #     BankAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Bank Account")    
    # bank_id = models.ForeignKey(
    #      Bank, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, related_name="Banks", verbose_name="Bank")    
    deposit_copy = models.FileField(
        upload_to='deposit_copy', verbose_name='Deposit copy', blank=True, null=True)
    is_cleared = models.CharField(max_length=50, choices=OPTIONS, blank=True, null=True)
    cleared_at = models.DateTimeField(
        max_length=255, blank=True, null=True, verbose_name="Cleared At")
    status = models.CharField(
        max_length=50, choices=STATUS, default='Created', blank=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)
    tax = models.PositiveBigIntegerField(blank=True, null=True)


    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Payment Out'

class BankTransferDetail(models.Model):
    transfer_type = models.CharField(
        max_length=50, choices=TRANSFER_TYPE, default='Deposit')
    mode = models.CharField(
        max_length=50, choices=MODE, null=True, blank=True,)
    deposit_type = models.CharField(
        max_length=50, choices=DEPOSIT_TYPE, null=True, blank=True)
    withdraw_type = models.CharField(
        max_length=50, choices=WITHDRAW_TYPE, null=True, blank=True)
    amount = models.PositiveBigIntegerField(blank=False, null=True)
    # bankaccount_id = models.ForeignKey(
    #     BankAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Bank Account")
    # from_bankaccount_id = models.ForeignKey(
    #     BankAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="From Bank Account", related_name="transfers_sent")        
    deposit_copy = models.FileField(
        upload_to='deposit_copy', verbose_name='Deposit copy', blank=True, null=True)
    payment_copy = models.FileField(
        upload_to='payment_copy', verbose_name='Payment copy', blank=True, null=True)
    cheque_no = models.CharField(max_length=255, blank=True, null=True)
    clearence_datetime = models.DateTimeField(
        max_length=255, blank=True, null=True, verbose_name="Clearence At")
    deposit_datetime = models.DateTimeField(
        max_length=255, blank=True, null=True, verbose_name="Deposit At")
    payment_datetime = models.DateTimeField(
        max_length=255, blank=True, null=True, verbose_name="Payment At")
    status = models.CharField(
        max_length=50, choices=STATUS, default='Created', blank=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Bank Transfer Detail'

class InvoiceAdjustment(models.Model):
    test_appointment_id = models.CharField(max_length=255, blank=False, null=True)
    tax = models.PositiveBigIntegerField(blank=False, null=True)
    total_adjustment = models.PositiveBigIntegerField(blank=False, null=True, default=0)
    invoive_datetime = models.DateTimeField(
        max_length=255, blank=True, null=True, verbose_name="Invoice Generated At")
    status = models.CharField(
        max_length=50, choices=STATUS, default='Created', blank=True)
    comments = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(
        max_length=255, blank=True, null=True, verbose_name="Invoice Adjustment At")
    price_discount = models.PositiveBigIntegerField(blank=False, null=True, default=0)
    others = models.PositiveBigIntegerField(blank=False, null=True, default=0)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Invoice Adjustment Form'

class ActivityLogFinance(models.Model):
    payment_in_id = models.ForeignKey(PaymentIn, on_delete=models.CASCADE, verbose_name='Payment in id', primary_key=False, null=True, blank=True)
    payment_out_id = models.ForeignKey(PaymentOut, on_delete=models.CASCADE, verbose_name='Payment out id', primary_key=False, null=True, blank=True)
    btd_id = models.ForeignKey(BankTransferDetail, on_delete=models.CASCADE, verbose_name='BTD id', primary_key=False, null=True, blank=True)
    invoice_adjustment_id = models.ForeignKey(InvoiceAdjustment, on_delete=models.CASCADE, verbose_name='Invoice Adjustment id', primary_key=False, null=True, blank=True)
    field_name = models.CharField(max_length=255, null= True)
    old_value = models.TextField(null= True)
    new_value = models.TextField(null= True)
    actions = models.CharField(
        max_length=50, choices= ACTIONS, default= 'Updated', verbose_name='Which action is performed?')
    user_id = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, verbose_name='Finance officer', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(
        max_length=50, choices= TYPE, default= 'Payment In', verbose_name='Form type?')
    payment_for = models.CharField(
        max_length=50, choices= PAYMENT_FOR_FINANCE, default= 'Lab', verbose_name='Payment for?')
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Activity Log Finance'
