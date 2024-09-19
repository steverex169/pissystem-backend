from datetime import datetime
from django.db import models
from organizationdata.models import Organization
from django.utils import timezone
from account.models import UserAccount
from databaseadmin.models import Analyte, Instrument, Method, Reagents, Scheme, Units, Cycle
from labowner.models import Lab

ACTIONS= (
    ('Updated', 'Updated'),
    ('Added', 'Added'),
    ('Deleted', 'Deleted'),
)
STATUS = (
    ('Created', 'Created'),
    ('Ready', 'Ready'),
    ('Open', 'Open'),
    ('Closed', 'Closed'),
    ('Report Available', 'Report Available'),
)
PAYMENT_STATUS = (
    ('Paid', 'Paid'),
    ('Unpaid', 'Unpaid'),)
RESULT_STATUS = (
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Accept', 'Accept'),
    ('Unapproved', 'Unapproved'),
    ('Cencel Request', 'Cencel Request'),
    ('Submitted', 'Submitted'),
)
# Option = (
#     ('Created', 'Created'),
#     ('Ready', 'Ready'),
#     ('Issued', 'Issued'),
#     ('Open', 'Open'),
#     ('Saved', 'Saved'),
#     ('Submitted', 'Submitted'),
#     ('Closed', 'Closed'),
#     ('Report Available', 'Report Available'),

# )

class Round(models.Model):
    account_id = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True)
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    rounds = models.PositiveBigIntegerField(blank=True, null=True) 
    scheme = models.ForeignKey(
        Scheme, on_delete=models.CASCADE, null=True, blank=True)
    cycle_no = models.CharField(max_length=255, blank=True, null=True)
    sample = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    closing_date = models.DateField(blank=True, null=True)
    participants = models.CharField(max_length=255, blank=True, null=True)
    # notes = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=STATUS, blank=True)

    def __str__(self):
        return self.status

    def save(self, *args, **kwargs):
        if self.pk is None:
            # New instance: Check if rounds, scheme, and cycle_no are set
            if self.rounds is not None and self.scheme is not None and self.cycle_no:
                self.status = 'Created'
        else:
            # Existing instance: Check if sample is added
            if self.sample and self.status == 'Created':
                self.status = 'Ready'
        super().save(*args, **kwargs)

    class Meta:       
        verbose_name = 'Round'
        
class SelectedScheme(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    participant = models.CharField(max_length=255, blank=False, null=True)
    cycle_id = models.ForeignKey(
        Cycle, on_delete=models.CASCADE, null=True, blank=True)
    # scheme_id =models.CharField(max_length=255, blank=False, null=True)
    added_at= models.DateTimeField(
        null=True, blank=True, verbose_name="Scheme added date")
    def __str__(self):
        return self.cycle_id

class Payment(models.Model):
    organization_id = models.ForeignKey(
         Organization, on_delete=models.CASCADE, null=True, blank=True)
    account_id = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    cycle_id = models.ForeignKey(
        Cycle, on_delete=models.CASCADE, null=True, blank=True)
    participant_id = models.ForeignKey(
        Lab, on_delete=models.CASCADE, null=True, blank=True)
    price = models.CharField(max_length=255,blank=False, null=True)
    discount = models.CharField(max_length=255,blank=False, null=True)
    photo = models.CharField(max_length=255, blank=False, null=True)
    paymentmethod = models.CharField(max_length=255,blank=True, null=True) 
    paydate = models.DateField(null=True, blank=True)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS, default='Unpaid')

    def __str__(self):
        return self.price

    class Meta:
        verbose_name = 'Payment'


class ActivityLogUnits(models.Model):
    
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='registrationadmin_activity_log_units', null=True, blank=True)
    round_id = models.ForeignKey(
        Round, on_delete=models.CASCADE, null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    closing_date = models.DateField(null=True, blank=True)
    old_value = models.TextField(null= True, blank=True)
    new_value = models.TextField(null= True, blank=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  
    date_of_updation = models.DateTimeField(blank=True, null=True, auto_now=True)
    field_name = models.CharField(max_length=255, null= True)
    actions = models.CharField(
        max_length=50, choices= ACTIONS, default= 'Added', verbose_name='Which action is performed?')
    status = models.CharField(
        max_length=50, choices=STATUS, blank=True)
    
    # type = models.CharField(
    #     max_length=50, choices= TYPE, default= 'Units', verbose_name='Form type?')
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'History'

class Statistics(models.Model):
    organization_id = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True)
    participant_id = models.ForeignKey(
        Lab, on_delete=models.CASCADE, null=True, blank=True)
    analyte = models.ForeignKey(Analyte, on_delete=models.CASCADE, null=True, blank=True)
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE, null=True, blank=True)
    lab_count = models.PositiveBigIntegerField(null=True, blank=True)
    mean_result = models.FloatField(null=True, blank=True)  
    median_result = models.FloatField(null=True, blank=True)  
    robust_mean = models.FloatField(null=True, blank=True)  
    std_deviation = models.FloatField(null=True, blank=True)  
    uncertainty = models.FloatField(null=True, blank=True)  
    cv_percentage = models.FloatField(null=True, blank=True)  
    z_scores_with_lab = models.JSONField(default=list, null=True, blank=True)
    z_scores_with_robust_mean = models.JSONField(default=list, null=True, blank=True)
    result = models.FloatField(blank=True, null=True)  
    rounds = models.PositiveBigIntegerField(blank=True, null=True) 
    unit_id = models.PositiveBigIntegerField(null=True, blank=True)
    instrument_id = models.PositiveBigIntegerField(null=True, blank=True)
    reagent_id = models.PositiveBigIntegerField(null=True, blank=True)
    method_id = models.PositiveBigIntegerField(null=True, blank=True)
    round_id = models.PositiveBigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Statistics'

    def __str__(self):
        return f"Results for {self.analyte.name} in Scheme {self.scheme.id}"

