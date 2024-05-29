from django.db import models
# from donor.models import Donor, DonorPayment

from labowner.models import Lab, LabPayment, OfferedTest
# from patient.models import Invoice, Payment, TestAppointment
# from b2bclient.models import B2BClient, B2BPayment, B2BShares
from financeofficer.models import PaymentIn, PaymentOut
# from financeadmin.models import Bank, BankAccount
# from corporate.models import Corporate


# Create your models here.
PAYMENT_METHOD = (
    ('Cash', 'Cash'),
    ('Cheque', 'Cheque'),
    ('Card', 'Card'),
    ('Donation', 'Donation'),
    # ('Corporate to Lab', 'Corporate to Lab'),
)

TRANSACTION_TYPE = (
    ('In', 'In'),
    ('Out', 'Out')
)
ACCOUNT_TYPE = (
    ('Lab', 'Lab'),
    ('In', 'In'),
    ('Out', 'Out')
)
PAYMENT_STATUS = (
    ('Not Paid', 'Not Paid'),
    ('Partially Paid', 'Partially Paid'),
    ('Paid', 'Paid'),
    ('Allocate','Allocate'),
    ('Created', 'Created'),
    ('Deposited', 'Deposited'),
    ('Cleared', 'Cleared'),
    ('Approved', 'Approved'),
    ('Unapproved', 'Unapproved'),
    ('Pending Clearance', 'Pending Clearance'),
    ('Bounced', 'Bounced'),
    ('Allocate', 'Allocate'),
    ('Cancel', 'Cancel'),
    ('Tax', 'Tax')

)
CANCEL_APPOINTMENT_STATUS = (
    ('Refund', 'Refund'),
    ('Not', 'Not')
)

STATUS = (
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Rejected', 'Rejected'),
    ('Pending Cancel', 'Pending Cancel'),
    ('Cancel', 'Cancel'),
    ('Sample Collected', 'Sample Collected'),
    ('Rescheduled', 'Rescheduled'),
    ('Result Uploaded', 'Result Uploaded'),
)


class AccountStatement(models.Model):
    # payment_id = models.ForeignKey(
    #     Payment, on_delete=models.CASCADE, primary_key=False, null=True, blank=False, verbose_name="Payment")
    lab_id = models.ForeignKey(
        Lab, on_delete=models.CASCADE, verbose_name='Lab', null=True)
    lab_payment_id = models.ForeignKey(
        LabPayment, on_delete=models.CASCADE, verbose_name='Lab Payment', null=True, blank=True)
    payment_in_id = models.ForeignKey(
        PaymentIn, on_delete=models.CASCADE, verbose_name='Payment In', null=True, blank=True)
    payment_out_id = models.ForeignKey(
        PaymentOut, on_delete=models.CASCADE, verbose_name='Payment Out', null=True, blank=True)
    # test_appointment_id = models.ForeignKey(
    #     TestAppointment, on_delete=models.CASCADE, primary_key=False, null=True, verbose_name="Appointment")
    order_id = models.CharField(max_length=255, blank=False, null=True)
    patient_name = models.CharField(max_length=255, blank=True, null=True)
    ordered_at = models.DateTimeField(null=True, blank=False)
    # payment_id = models.ForeignKey(
        # Payment, on_delete=models.CASCADE, primary_key=False, null=True, verbose_name="Payment")
    dues_before_discount = models.PositiveIntegerField(blank=False, null=True, default=0)
    total_dues_before_discount = models.PositiveIntegerField(blank=False, null=True, default=0)
    dues = models.PositiveIntegerField(blank=False, null=True, default=0)
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD, default='Cash', blank=False, null=True)
    is_settled = models.BooleanField(default=0, blank=False, null=True)
    payable = models.FloatField(null=True, blank=True, default=0)
    Receivable = models.FloatField(null=True, blank=True, default=0)
    labhazir_share = models.FloatField(null=True, blank=True, default=0)
    lab_share = models.FloatField(null=True, blank=True, default=0)
    lab_total_discount_percentage = models.FloatField(null=True, blank=True, default=0)
    discounted_by_lab = models.FloatField(null=True, blank=True, default=0)
    discounted_by_labhazir = models.FloatField(null=True, blank=True, default=0)
    received_payment_labHazir = models.PositiveIntegerField(blank=False, null=True, default=0)
    received_payment_lab = models.PositiveIntegerField(blank=False, null=True, default=0)
    referral_remaining_fee_margin = models.FloatField(null=True, blank=True, default=0)
    lab_remaining_fee_margin = models.FloatField(null=True, blank=True, default=0)
    transaction_type = models.CharField(
        max_length=50, choices=TRANSACTION_TYPE, null=True, blank=False)
    sample_collector_amount = models.PositiveIntegerField(blank=False, null=True, default=0)
    status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS, default='Not Paid')   
    cancel_appintment_status = models.CharField(
        max_length=50, choices=CANCEL_APPOINTMENT_STATUS, null=True, blank=True) 
    paid_at = models.DateTimeField(max_length=255, null=True, blank=True)
         # cheque_number = models.CharField(max_length=255, blank=True, null=True)
    is_transaction_completed = models.BooleanField(
        default=0, blank=False, null=True)
    statement = models.PositiveIntegerField(blank=False, null=True, default=0)
    generated_at = models.DateTimeField(null=True, blank=True)
    account_type = models.CharField(
        max_length=50, choices=ACCOUNT_TYPE, null=True, blank=False)
    lab_counter_discount = models.PositiveIntegerField(blank=False, null=True, default=0)
    tax = models.CharField(max_length=255, blank=True, null=True)
    tax_amount = models.PositiveIntegerField(blank=False, null=True, default=0)


    def __str__(self):
        return self.lab_id.name

    class Meta:
        verbose_name = 'Lab Account Statement'


class DonorAccountStatement(models.Model):
    # donor_id = models.ForeignKey(
    #     Donor, on_delete=models.CASCADE, verbose_name='Donor', null=True)
    payment_in_id = models.ForeignKey(
        PaymentIn, on_delete=models.CASCADE, verbose_name='Payment In', null=True, blank=True)
    # test_appointment_id = models.ForeignKey(
    #     TestAppointment, on_delete=models.CASCADE, primary_key=False, null=True, verbose_name="Appointment", blank=True)
    order_id = models.CharField(max_length=255, blank=True, null=True)
    patient_name = models.CharField(max_length=255, blank=True, null=True)
    lab_name = models.CharField(max_length=255, blank=True, null=True)
    lab_city = models.CharField(max_length=255, blank=True, null=True)
    ordered_at = models.DateTimeField(null=True, blank=True)
    # payment_id = models.ForeignKey(
        # Payment, on_delete=models.CASCADE, primary_key=False, null=True, verbose_name="Payment", blank=True)
    opening_amount = models.PositiveBigIntegerField(blank=False, null=True)
    current_amount = models.PositiveBigIntegerField(blank=True, null=True, default=0)
    # test_appointment_id = models.ForeignKey(
    #     TestAppointment, on_delete=models.CASCADE, primary_key=False, null=True, verbose_name="Appointment", blank=True)
    balance = models.PositiveBigIntegerField(blank=True, null=True)
    both_id = models.PositiveBigIntegerField(blank=True, null=True)
    Debit = models.PositiveBigIntegerField(blank=True, null=True, default=0)
    Credit = models.PositiveBigIntegerField(blank=True, null=True, default=0)
    transaction_type = models.CharField(
        max_length=50, choices=TRANSACTION_TYPE, null=True, blank=False)
    is_transaction_completed = models.BooleanField(
        default=0, blank=False, null=True)
    is_settled = models.BooleanField(default=0, blank=False, null=True)
    generated_at = models.DateTimeField(null=True, blank=False)
    payment_method = models.CharField(
        max_length=50,blank=False, null=True)
    # status = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS, default='Not Paid')   
    paid_at = models.DateTimeField(max_length=255, null=True, blank=True)
    cleared_at = models.DateTimeField(max_length=255, null=True, blank=True)
    cancel_appintment_status = models.CharField(
        max_length=50, choices=CANCEL_APPOINTMENT_STATUS, null=True, blank=True) 

    def __str__(self):
        return self.donor_id

    # class Meta:
    #     verbose_name = 'Donor Account Statement'
        


class B2BAccountStatement(models.Model):
    # payment_id = models.ForeignKey(
    #     Payment, on_delete=models.CASCADE, primary_key=False, null=True, blank=False, verbose_name="Payment")
    # b2b_id = models.ForeignKey(
    #     B2BClient, on_delete=models.CASCADE, verbose_name='B2B', null=True)
    payment_out_id = models.ForeignKey(
        PaymentOut, on_delete=models.CASCADE, verbose_name='Payment In', null=True, blank=True)
    offered_test_id = models.ForeignKey(
        OfferedTest, on_delete=models.CASCADE, primary_key=False, null=True, blank=False)
    # test_appointment_id = models.ForeignKey(
    #     TestAppointment, on_delete=models.CASCADE, primary_key=False, null=True, verbose_name="appointment", blank=True)
    b2b_share = models.FloatField(null=True, blank=True, default=0)
    order_id = models.CharField(max_length=255, blank=True, null=True)
    ordered_at = models.DateTimeField(null=True, blank=True)
    amount = models.PositiveIntegerField(blank=False, null=True)
    patient_name = models.CharField(max_length=255, blank=True, null=True)
    lab_name = models.CharField(max_length=255, blank=True, null=True)
    transaction_type = models.CharField(
        max_length=50, choices=TRANSACTION_TYPE, null=True, blank=False)
    is_transaction_completed = models.BooleanField(
        default=0, blank=False, null=True)
    is_settled = models.BooleanField(default=0, blank=False, null=True)
    generated_at = models.DateTimeField(null=True, blank=False)
    payment_method = models.CharField(
        max_length=50,blank=False, null=True)
    status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS, default='Not Paid')
    paid_at = models.DateTimeField(max_length=255, null=True, blank=True)
    labhazir_share = models.FloatField(null=True, blank=True, default=0)
    Credit = models.FloatField(null=True, blank=True, default=0)
    Debit = models.FloatField(null=True, blank=True, default=0)

    def __str__(self):
        return str(self.b2b_id)

    class Meta:
        verbose_name = 'B2B Account Statement'
    
class BankAccountStatement(models.Model):
    # bankaccount_id = models.ForeignKey(
    #     BankAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Bank Account")  
    payment_in= models.CharField(max_length=255, blank=False, null=True)
    b2b_id = models.CharField(max_length=255, blank=False, null=True)
    advertisement_id = models.CharField(max_length=255, blank=False, null=True)
    payment_out= models.CharField(max_length=255, blank=False, null=True)
    amount = models.PositiveIntegerField(blank=False, null=True)
    lab_id = models.CharField(max_length=255, blank=False, null=True)
    status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS, default='Not Paid')
    Credit = models.FloatField(null=True, blank=True, default=0)
    Debit = models.FloatField(null=True, blank=True, default=0)
    transaction_type = models.CharField(
        max_length=50, choices=TRANSACTION_TYPE, null=True, blank=False)
    balance = models.BigIntegerField(blank=True, null=True, default=0)
    date = models.DateTimeField(max_length=255, null=True, blank=True)


    def __str__(self):
        return str(self.bankaccount_id)

    class Meta:
        verbose_name = 'BANK Account Statement'
class CorporateLabStatement(models.Model):

    # corporate_id = models.ForeignKey(
    #     Corporate, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Corporate ID")  
    payment_in= models.CharField(max_length=255, blank=False, null=True)
    # test_appointment_id = models.ForeignKey(
    #     TestAppointment, on_delete=models.CASCADE, primary_key=False, null=True, verbose_name="Appointment")
    lab_id = models.ForeignKey(
        Lab, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Lab ID")    
    amount = models.PositiveIntegerField(blank=False, null=True)
    appointment_status = models.CharField(
        max_length=50, choices=STATUS, default='Pending', null=True)
    status = models.CharField(
        max_length=50, choices=PAYMENT_STATUS, default='Not Paid')
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD, default='Cash', blank=False, null=True)
    payable = models.FloatField(null=True, blank=True, default=0)
    plateform_fees = models.FloatField(null=True, blank=True, default=0)
    Receivable = models.FloatField(null=True, blank=True, default=0)
    is_settled = models.BooleanField(default=0, blank=False, null=True)
    order_id = models.CharField(max_length=255, blank=False, null=True)
    generated_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(max_length=255, null=True, blank=True)
    corporate_employee_id = models.CharField(max_length=255, blank=False, null=True)
    def __str__(self):
        return str(self.corporate_id)

    # class Meta:
    #     verbose_name = 'Corporate Lab Account Statement'