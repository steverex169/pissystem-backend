
from account.models import UserAccount
from django.db import models
from organizationdata.models import Organization
from django.utils import timezone
from account.models import UserAccount

class City(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Participant City'

