from django.db import models
from organization.models import Organization
from django.utils import timezone
from account.models import UserAccount
from databaseadmin.models import Scheme
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
    participants = models.ManyToManyField(Lab, blank=True)
    issue_date = models.DateField(blank=True, null=True)
    closing_date = models.DateField(blank=True, null=True)
    # notes = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=STATUS, blank=True)

    @property
    def nooflabs(self):
        return self.participants.count()

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

