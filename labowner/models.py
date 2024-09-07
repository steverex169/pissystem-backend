from datetime import datetime
from enum import unique
from django.db import models
from typing import Type
from account.models import UserAccount
from organizationdata.models import Organization
# from donor.models import DonorBank
# from medicaltest.models import Test, Unit
from staff.models import Marketer, Staff
from territories.models import Territories
from django.utils.timezone import now
from databaseadmin.models import Analyte, Instrument, Method, Units, Reagents, Scheme

# from corporate.models import Corporate


# Create your models here.
OPTIONS = (
    ('Yes', 'Yes'),
    ('No', 'No')
)

APPOINTMENTSOPTIONS = (
    ('Main', 'Main'),
    ('Collection', 'Collection'),
    ('Both', 'Both')
)
DAYS_OF_WEEK = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )
DURATION_TYPE = (
    ('days', 'days'),
    ('hours', 'hours')
)
TEST_CATEGORIES = (
    ('Chem & immuno', 'Chem & immuno'),
    ('Microbiology', 'Microbiology'),
    ('Hematology', 'Hematology'),
    ('Molecular', 'Molecular'),
    ('Histopathology', 'Histopathology'),
    ('Blood Bank-Transfusion Medicine', 'Blood Bank-Transfusion Medicine'),
)
SAMPLE_TYPE = (
    ('Whole blood', 'Whole blood'),
    ('Blood (Aerobic Culture Bottle)','Blood (Aerobic Culture Bottle)'),
    ('Serum (Gel / Yellow Vial)', 'Serum (Gel / Yellow Vial)'),
    ('Tissue', 'Tissue'),
    ('Plasma (Sodium Floride / Gray Tube)', 'Plasma (Sodium Floride / Gray Tube)'),
    ('Plasma (Sodium Citrate / Blue Vial)', 'Plasma (Sodium Citrate / Blue Vial)'),
    ('Plasma (EDTA / Purple Tube)', 'Plasma (EDTA / Purple Tube)'),
    ('Plasma (Heparin / Green Tube)', 'Plasma (Heparin / Green Tube)'),
    ('Biopsy', 'Biopsy'),
    ('Swab', 'Swab'),
    ('Urine', 'Urine'),
    ('Stool', 'Stool'),
    ('Semen', 'Semen'),
    ('CSF', 'CSF'),
    ('Sputum', 'Sputum'),  
    ('Body Fluid', 'Body Fluid'),   
    ('Others', 'Others'),   
)

LAB_TYPE = (
    ('Main Lab', 'Main Lab'),
    ('Collection Point', 'Collection Point')
)

FINANCIAL_SETTLEMENT = (
    ('Self', 'Self'),
    ('Main Lab', 'Main Lab')
)

STATUS = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Accept', 'Accept'),
    ('Unapproved', 'Unapproved'),
    ('Cencel Request', 'Cencel Request'),
    ('Cencel', 'Cencel'),
)
PAYMENT_STATUS = (
    ('Paid', 'Paid'),
    ('Unpaid', 'Unpaid'),
)
MEMBERSHIP_STATUS = (
    ('Active', 'Active'),
    ('Suspended', 'Suspended'),
)
GENDER = (
    ('Male', 'Male'),
    ('Female', 'Female')
)

CERTIFICATE_TYPE = (
    ('Lab', 'Lab'),
    # ('Test', 'Test'),
)

REGISTERED_BY = (
    ('Lab', 'Lab'),
    ('Marketer', 'Marketer'),
)

TEST_PERFORMING_METHOD = (
    ('In House', 'In House'),
    ('Outsource', 'Outsource'),
)

HEALTH_DEPT = (
    ('Islamabad Health Regulatory Authority',
     'Islamabad Health Regulatory Authority'),
    ('Punjab Healthcare Comission', 'Punjab Healthcare Comission'),
    ('Sindh Healthcare Comission', 'Sindh Healthcare Comission'),
    ('Balochistan Healthcare Comission', 'Balochistan Healthcare Comission'),
    ('KPK Healthcare Comission', 'KPK Healthcare Comission'),
    ('AJ&K Healthcare Comission', 'AJ&K Healthcare Comission'),
    ('Gilgit Baltistan Health Department', 'Gilgit Baltistan Health Department'),
)
BANK = (
    ('Askari Bank', 'Askari Bank'),
    ('Allied Bank', 'Allied Bank'),
    ('Bank Al Habib Limited', 'Bank Al Habib Limited'),
    ('Bank Alfalah', 'Bank Alfalah'),
    ('MCB Bank Limited', 'MCB Bank Limited'),
    ('HBL / Konnect', 'HBL / Konnect'),
    ('MCB Islamic', 'MCB Islamic'),
    ('Meezan Bank', 'Meezan Bank'),
    ('National Bank of Pakistan(NBP)', 'National Bank of Pakistan(NBP)'),
    ('Soneri Bank', 'Soneri Bank'),
    ('United Bank Limited', 'United Bank Limited'),
)

PAYMENT_METHOD = (
    ('Cash', 'Cash'),
    ('Cheque', 'Cheque'),
    ('Card', 'Card'),
)
CURRENCY = (
    ('Cash', 'Cash'),
    ('Cheque', 'Cheque'),
    ('Card', 'Card'),
)
ADDRESS_TYPE = (
    ('Pick from', 'Pick from'),
    ('Deliever to', 'Deliever to'),
)
OFFICE = (
    ('Central Office', 'Central Office'),
    ('North Office', 'North Office'),
    ('South Office', 'South Office'),
)
TEST_CATEGORIES = (
    ('Chem & immuno', 'Chem & immuno'),
    ('Microbiology', 'Microbiology'),
    ('Hematology', 'Hematology'),
    ('Molecular', 'Molecular'),
    ('Histopathology', 'Histopathology'),
    ('Blood Bank-Transfusion Medicine', 'Blood Bank-Transfusion Medicine'),
)
SAMPLE_TYPE = (
    ('Whole blood', 'Whole blood'),
    ('Blood (Aerobic Culture Bottle)','Blood (Aerobic Culture Bottle)'),
    ('Serum (Gel / Yellow Vial)', 'Serum (Gel / Yellow Vial)'),
    ('Tissue', 'Tissue'),
    ('Plasma (Sodium Floride / Gray Tube)', 'Plasma (Sodium Floride / Gray Tube)'),
    ('Plasma (Sodium Citrate / Blue Vial)', 'Plasma (Sodium Citrate / Blue Vial)'),
    ('Plasma (EDTA / Purple Tube)', 'Plasma (EDTA / Purple Tube)'),
    ('Plasma (Heparin / Green Tube)', 'Plasma (Heparin / Green Tube)'),
    ('Biopsy', 'Biopsy'),
    ('Swab', 'Swab'),
    ('Urine', 'Urine'),
    ('Stool', 'Stool'),
    ('Semen', 'Semen'),
    ('CSF', 'CSF'),
    ('Sputum', 'Sputum'),  
    ('Body Fluid', 'Body Fluid'),   
    ('Others', 'Others'),   
)
ACTIONS= (
    ('Updated', 'Updated'),
    ('Added', 'Added'),
    ('Deleted', 'Deleted'),
)
PAYMENT_STATUS=(
    ('Paid', 'Paid'),
    ('Unpaid', 'Unpaid')
)
MEMBERSHIP_STATUS=(
    ('Active', 'Active'),
    ('Suspended', 'Suspended')
)

RESULT_STATUS = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Accept', 'Accept'),
    ('Unapproved', 'Unapproved'),
    ('Cencel Request', 'Cencel Request'),
    ('Submited', 'Submited'),
)
class Lab(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    staff_id = models.ForeignKey(
        Staff, on_delete=models.CASCADE, null=True, blank=True)
    account_id = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, primary_key=False, null=True)
    name = models.CharField(max_length=255, blank=False,
                            null=True, verbose_name='Lab name')
    user_name = models.CharField(max_length=255, blank=False,
                            null=True, verbose_name='user name')
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS, default='Unpaid')
    membership_status = models.CharField(max_length=50, choices=MEMBERSHIP_STATUS, default='Suspended')
    
    financial_settlement = models.CharField(
        max_length=50, choices=FINANCIAL_SETTLEMENT, default='Self', blank=True, null=True)
    logo = models.ImageField(
        upload_to='logo', verbose_name='Logo', blank=True, null=True)
    lab_experience = models.PositiveIntegerField(
        blank=True, null=True, verbose_name='Lab Experience (Years)')
    email = models.EmailField(max_length=70, blank=False,  null=True)
    email_participant = models.EmailField(max_length=70, blank=False,  null=True)
    phone = models.CharField(max_length=255, blank=True, null=True,
                             verbose_name='Phone', help_text="Please use the format: +923123456789")
    landline = models.CharField(
        max_length=20, blank=False, null=True, help_text="Please use the format: +922134552799")
    fax = models.CharField(
        max_length=20, blank=False, null=True, help_text="Please use the format: + (Country Code) (City Code without the leading zero) (fax number)")
    address = models.CharField(max_length=255, blank=False, null=True, verbose_name='Address',
                               help_text='Please enter your address to automatically locate it on map.')
    billing_address = models.CharField(max_length=255, blank=True, null=True)
    shipping_address = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    registered_at = models.DateTimeField(null=True, blank=False)
    registered_by = models.CharField(
        max_length=50, choices=REGISTERED_BY, default='Lab')
    lab_staff_name = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='Registered by (Name)')
    lab_staff_designation = models.CharField(
        max_length=255, blank=True, null=True, verbose_name='Designation')
    marketer_id = models.ForeignKey(
        Marketer, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Marketer")
    status = models.CharField(
        max_length=50, choices=STATUS, default='Pending')
    # done_by = models.ForeignKey(
    #     Staff, on_delete=models.CASCADE, primary_key=False, null=True, blank=True, verbose_name="Approved/Unapproved by")
    done_at = models.DateTimeField(
        max_length=255, blank=True, null=True, verbose_name="Approved/Unapproved at")
    postalcode = models.CharField(
        max_length=255, null=True, blank=True)
    organization = models.CharField(max_length=255, null=True, blank=True, verbose_name="organization name")
   
    is_active = models.CharField(max_length=50, choices=OPTIONS, default='Yes',
                                 null=True, verbose_name='Is lab active for the services?')
   
    is_blocked = models.CharField(max_length=50, choices=OPTIONS, default='No',
       null=True, verbose_name='Is lab blocked from using our services?')
    is_temporary_blocked = models.CharField(max_length=50, choices=OPTIONS, default='No',
       null=True, verbose_name='Is lab temporary blocked from using our services?')
    is_approved = models.BooleanField(default=0, blank=False, null=True)
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name='Website')
    district = models.CharField(max_length=255, blank=True, null=True)
    landline_registered_by = models.CharField(
        max_length=30, blank=False, null=True, help_text="Please use the format: +922134552799")
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS, default='Unpaid')
    membership_status = models.CharField(max_length=50, choices=MEMBERSHIP_STATUS, default='Suspended')
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Lab'

class Pathologist(models.Model):
    lab_id = models.ForeignKey(
        Lab, on_delete=models.CASCADE, verbose_name='Lab name', null=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    email = models.EmailField(max_length=255, blank=False, null=True)
    phone = models.CharField(max_length=255, blank=False, null=True,
                             help_text="Please use the format: +923123456789", verbose_name='Phone')
    landline = models.CharField(
        max_length=13, blank=True, null=True, help_text="Please use the format: +922134552799")
    photo = models.ImageField(
        upload_to='pathologist', verbose_name='Photo', blank=False, null=True)
    pmdc_reg_no = models.CharField(max_length=255, blank=False, null=True)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    speciality = models.CharField(max_length=255, blank=True, null=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    is_available_for_consultation = models.CharField(
        max_length=50, choices=OPTIONS, default='Yes', verbose_name='Is available for online consultation?')
    is_available_on_whatsapp = models.CharField(
        max_length=50, choices=OPTIONS, default='Yes', verbose_name='Are you available on WhatsApp?')
    is_associated_with_pap = models.CharField(
        max_length=50, choices=OPTIONS, blank=True, null=True, verbose_name='Are you associated with PAP?')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Pathologist'


class SampleCollector(models.Model):
    account_id = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True)
    lab_id = models.ForeignKey(
        Lab, on_delete=models.CASCADE, verbose_name='Lab name', null=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    gender = models.CharField(
        max_length=50, choices=GENDER, default='Male', blank=False, null=True)
    cnic = models.CharField(max_length=255, blank=False, null=True,
                            verbose_name='CNIC', help_text='Please use the format XXXXX-XXXXXXX-X')
    photo = models.ImageField(
        upload_to='samplecollectors', verbose_name='Sample Collector\'s Photo')
    phone = models.CharField(max_length=255, blank=False, null=True,
                             help_text='Please use the format: +923123456789')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Home Sample Collector'

class LabCorporate(models.Model):
    lab_id = models.ForeignKey(
        Lab, on_delete=models.CASCADE, verbose_name='Lab name', null=True)
    # corporate_id = models.ForeignKey(Corporate, on_delete=models.CASCADE,
    #                             primary_key=False, verbose_name='Corporate name', null=True)
    shared_percentage = models.FloatField(
        null=True, blank=True, verbose_name="Referral Fee Percentage", default=0.02)
    status = models.CharField(
        max_length=50, choices=STATUS, default='Pending')
    remaining_amount = models.PositiveIntegerField(blank=False, null=True, default=0)
    allow_all = models.CharField(max_length=50, choices=OPTIONS, default='No',
                                 null=True)
    def __str__(self):
        return self.lab_id.name + " - " + self.corporate_id.name 

    # class Meta:
    #     verbose_name = 'Lab Corporate'


# class QualityCertificate(models.Model):
#     lab_id = models.ForeignKey(
#         Lab, on_delete=models.CASCADE, verbose_name='Lab name', null=True)
#     certificate_type = models.CharField(max_length=255, blank=False,
#                                         null=True, verbose_name='Certificate type')
#     sub_certificate_type = models.CharField(max_length=255, blank=False,
#                                         null=True, verbose_name='Sub Certificate type')
#     name = models.CharField(max_length=255, blank=False,
#                             null=True, verbose_name='Certificate title')
#     type = models.CharField(
#         max_length=50, choices=CERTIFICATE_TYPE, default='Lab', blank=False, null=True, verbose_name='Certificate is for')
#     certificate = models.FileField(upload_to='testcertificates', null=True)
#     expiry_date = models.DateField(null=True, blank=True)
#     start_date = models.DateField(null=True, blank=True)
#     end_date = models.DateField(null=True, blank=True)


#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = 'Quality Certificate'


class LabPayment(models.Model):
    lab_id = models.ForeignKey(
        Lab, on_delete=models.CASCADE, verbose_name='Lab', null=True)
    invoice_id = models.CharField(
        max_length=5, unique=True, null=True, blank=False)
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD, default='Cash')
    address_type = models.CharField(
        max_length=50, choices=ADDRESS_TYPE, null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    amount = models.PositiveBigIntegerField(blank=False, null=True)
    paid_at = models.DateTimeField(max_length=255, null=True, blank=True)
    cheque_no = models.CharField(max_length=255, blank=True, null=True)
    cheque_image = models.ImageField(
        upload_to='cheque', verbose_name='Cheque Image', blank=True, null=True)
    deposited_at = models.DateTimeField(max_length=255, null=True, blank=True)
    # deposit_bank = models.ForeignKey(
    #     DonorBank, on_delete=models.CASCADE, verbose_name='Bank', null=True)
    deposit_slip = models.ImageField(
        upload_to='deposit_slip', verbose_name='Deposit Slip', blank=True, null=True)
    is_cleared = models.BooleanField(default=0, blank=True, null=True)
    cleared_at = models.DateTimeField(max_length=255, null=True, blank=True)
    is_settled = models.BooleanField(default=0, blank=True, null=True)
    settled_at = models.DateTimeField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.invoice_id

    class Meta:
        verbose_name = 'Lab Payment'

class ActivityLog(models.Model):
    field_name = models.CharField(max_length=255, null= True)
    old_value = models.TextField(null= True)
    new_value = models.TextField(null= True)
    old_discount_by_lab = models.TextField(null= True)
    new_discount_by_lab =  models.TextField(null= True)
    start_date_by_lab = models.DateTimeField(max_length=255, null=True, blank=True)
    end_date_by_lab = models.DateTimeField(max_length=255, null=True, blank=True, default=datetime.now)
    old_discount_by_labhazir = models.TextField(null= True)
    new_discount_by_labhazir = models.TextField(null= True)
    start_date_by_labhazir = models.DateTimeField(max_length=255, null=True, blank=True)
    end_date_by_labhazir = models.DateTimeField(max_length=255, null=True, blank=True, default=datetime.now)
    actions = models.CharField(
        max_length=50, choices=ACTIONS, default= 'Updated', verbose_name='Which action is performed?')
    user = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, verbose_name='Lab name', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username + " - " + self.offered_test_id.test_id.name
    class Meta:
         verbose_name = 'Activity Log'

# Database of Manufactural
# class Manufactural(models.Model):
#     organization_id = models.ForeignKey(
#         Organization, on_delete=models.CASCADE, null=True, blank=True)
#     name = models.CharField(max_length=255, blank=False, null=True) 
#     landline = models.CharField(
#         max_length=13, blank=True, null=True, help_text="Please use the format: +922134552799")
#     # added_by = models.ForeignKey(
#     #     UserAccount, on_delete=models.CASCADE, verbose_name='added by', null=True)
#     date_of_addition = models.DateTimeField(max_length=255, null=True, blank=True, default=datetime.now)
#     address = models.CharField(max_length=255, blank=False, null=True, verbose_name='Address')
#     city = models.CharField(max_length=255, blank=True, null=True)
#     country = models.CharField(max_length=255, blank=True, null=True)
#     def __str__(self):
#         return self.name
#     class Meta:
#         verbose_name = 'Manufactural'

# Database of Result
class Result(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    scheme_id = models.CharField(max_length=255, blank=True, null=True)
    lab_id = models.ForeignKey(Lab, on_delete=models.CASCADE, verbose_name='Lab', primary_key=False, null=True, blank=False)
    analyte = models.ForeignKey(Analyte, on_delete=models.CASCADE, verbose_name='Analyte', primary_key=False, null=True, blank=False)
    units = models.ForeignKey(Units, on_delete=models.CASCADE, verbose_name='Units', primary_key=False, null=True, blank=False)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, verbose_name='Instrument', primary_key=False, null=True, blank=False)
    method = models.ForeignKey(Method, on_delete=models.CASCADE, verbose_name='Method', primary_key=False, null=True, blank=False)
    reagents = models.ForeignKey(Reagents, on_delete=models.CASCADE, verbose_name='Reagents', primary_key=False, null=True, blank=False)
    # result = models.CharField(max_length=255, blank=True, null=True)
    result = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Updated to DecimalField
    result_status = models.CharField(
        max_length=50, choices=RESULT_STATUS, default='Pending')
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True ) # Automatically set to now every time the object is saved
    # updated_at= models.DateTimeField(null=True, blank=True, default=datetime.now)
    rounds = models.PositiveBigIntegerField(blank=True, null=True) 

    def __str__(self):
        # return self.result
        return str(self.result) if self.result is not None else 'No Result'
    class Meta:
        verbose_name = 'Result'