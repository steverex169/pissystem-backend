
from account.models import UserAccount
from django.db import models
from organization.models import Organization
from django.utils import timezone

from staff.models import Staff
# table of units
ACTIONS= (
    ('Updated', 'Updated'),
    ('Added', 'Added'),
    ('Deleted', 'Deleted'),
)
STATUS = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
)
TYPE= (
    ('Units', 'Units'),
    ('Instruments', 'Instruments'),
    ('Reagent', 'Reagent'),
    ('Method', 'Method'),
    ('Manufactural', 'Manufactural'),
    ('Analyte', 'Analyte'),
    ('Instrumentlist', 'Instrumentlist')
    )
class Units(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    formula = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Database Unit'

class Manufactural(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=False, null=True)
    telephone = models.CharField(max_length=255, blank=True, null=True)
    city =models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True) 
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Database Manufactural'

class Method(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    code = models.PositiveBigIntegerField(blank=True, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True) 
    status = models.CharField(
        max_length=50, choices=STATUS, default='Inactive', blank=True)
    def __str__(self):
        return self.name

    class Meta:       
        verbose_name = 'Method'

# class Analyte(models.Model):
#     organization_id = models.ForeignKey(
#         Organization, on_delete=models.CASCADE, null=True, blank=True)
#     name = models.CharField(max_length=255, blank=True, null=True)
#     code = models.PositiveBigIntegerField(blank=True, null=True)
#     date_of_addition = models.DateTimeField(blank=True, null=True) 
#     status = models.CharField(
#         max_length=50, choices=STATUS, default='Inactive', blank=True)
#     def __str__(self):
#         return self.name

#     class Meta:       
#         verbose_name = 'Analyte'

class Reagents(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    code = models.PositiveBigIntegerField(blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True) 
    status = models.CharField(
        max_length=50, choices=STATUS, default='Inactive', blank=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Database Reagent'

class InstrumentType(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False,
                            null=True, verbose_name='Instrument type')
    date_of_addition = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Instrument type'

class Instrument(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    instrument_type = models.ForeignKey(
        InstrumentType, on_delete=models.SET_NULL, null=True, blank=True)
    manufactural = models.ForeignKey(
        Manufactural, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False,
                            null=True, verbose_name='Instrument')
    code = models.PositiveBigIntegerField(blank=False, null=True)
    date_of_addition = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS, default='Inactive', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Instrument'
        
class Analyte(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    code = models.PositiveBigIntegerField(blank=True, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)
    method = models.ForeignKey(
        Method, on_delete=models.SET_NULL, null=True, blank=True)
    instrument = models.ForeignKey(
        Instrument, on_delete=models.SET_NULL, null=True, blank=True)
    reagents = models.ManyToManyField(Reagents, blank=True)  # Change to ManyToManyField
    unit = models.ForeignKey(
        Units, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS, default='Inactive', blank=True)
   
    master_unit = models.ForeignKey(
        Units, on_delete=models.SET_NULL, related_name="master_unit", null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Analyte'


class ActivityLogUnits(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    analyte_id = models.ForeignKey(
         Analyte, on_delete=models.CASCADE, null=True, blank=True)
    manufactural_id = models.ForeignKey(
         Manufactural, on_delete=models.CASCADE, null=True, blank=True)
    reagent_id = models.ForeignKey(
         Reagents, on_delete=models.CASCADE, null=True, blank=True)
    unit_id = models.ForeignKey(
        Units, on_delete=models.CASCADE, null=True, blank=True)
    instrumenttype_id = models.ForeignKey(
        InstrumentType, on_delete=models.CASCADE, null=True, blank=True)
    instrument_id = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, null=True, blank=True)
    method_id = models.ForeignKey(
        Method, on_delete=models.CASCADE, null=True, blank=True)
    old_value = models.TextField(null= True, blank=True)
    new_value = models.TextField(null= True, blank=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  
    date_of_updation = models.DateTimeField(blank=True, null=True, auto_now=True)
    field_name = models.CharField(max_length=255, null= True)
    actions = models.CharField(
        max_length=50, choices= ACTIONS, default= 'Added', verbose_name='Which action is performed?')
    status = models.CharField(
        max_length=50, choices=STATUS, default='Inactive', blank=True)
    type = models.CharField(
        max_length=50, choices= TYPE, default= 'Units', verbose_name='Form type?')
    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'History'

class News(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    added_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, blank=False, null=True)
    description = models.TextField()
    picture = models.ImageField(upload_to='news_pictures/', blank=True, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True) 
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'News'