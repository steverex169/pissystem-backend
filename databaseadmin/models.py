
from account.models import UserAccount
from django.db import models
from organization.models import Organization
from django.utils import timezone
from account.models import UserAccount

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
CYCLE = (
    ('Months', 'Months'),
    ('Year', 'Year'),
)
TYPE= (
    ('Units', 'Units'),
    ('Instruments', 'Instruments'),
    ('Reagent', 'Reagent'),
    ('Method', 'Method'),
    ('Manufactural', 'Manufactural'),
    ('Analyte', 'Analyte'),
    ('Instrumentlist', 'Instrumentlist'),
    ('City', 'City'),
    ('ParticipantCountry','ParticipantCountry'),
    ('ParticipantProvince','ParticipantProvince'),
    ('District', 'District'),
    ('Department', 'Department'),
    ('Designation', 'Designation'),
    ('ParticipantType', 'ParticipantType'),
    ('ParticipantSector', 'ParticipantSector'),
    )

class City(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Participant City'

class ParticipantCountry(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Participant Country'

class ParticipantProvince(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Participant Province'

class District(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Participant District'

class Department(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Participant Department'

class Designation(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Participant Designation'

class ParticipantType(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Participant Type'

class ParticipantSector(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Participant Sector'

class Units(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  # Changed to DateTimeField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Database Unit'

class Manufactural(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    country = models.ForeignKey(
        ParticipantCountry, on_delete=models.SET_NULL, null=True, blank=True)
    website =models.CharField(max_length=10000000, blank=False, null=True)
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


class Reagents(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    code = models.PositiveBigIntegerField(blank=False, null=True)
    date_of_addition = models.DateTimeField(blank=True, null=True) 
    manufactural = models.ForeignKey(
        Manufactural, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(
        ParticipantCountry, on_delete=models.SET_NULL, null=True, blank=True)
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
    country = models.ForeignKey(
        ParticipantCountry, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255, blank=False,
                            null=True, verbose_name='Instrument')
    code = models.PositiveBigIntegerField(blank=False, null=True)
    model = models.CharField(max_length=255, blank=False, null=True)
    
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
    methods = models.ManyToManyField(Method, blank=True)
    instruments = models.ManyToManyField(Instrument, blank=True)
    reagents = models.ManyToManyField(Reagents, blank=True)
    units = models.ManyToManyField(Units, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS, default='Inactive', blank=True)
    master_unit = models.ForeignKey(
        Units, on_delete=models.SET_NULL, related_name="master_unit", null=True, blank=True)
    
    @property
    def noofreagents(self):
        return self.reagents.count()
    
    @property
    def master_unit_name(self):
        return self.master_unit.name if self.master_unit else None

    def noofmethods(self):
        return self.methods.count()

    def noofinstruments(self):
        return self.instruments.count()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Analyte'

class Scheme(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    added_by= models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, null=True, blank=True) 
    
    date_of_addition = models.DateTimeField(blank=True, null=True) 
    status = models.CharField(
        max_length=50, choices=STATUS, default='Inactive', blank=True)
    def __str__(self):
        return self.name

    class Meta:       
        verbose_name = 'Scheme'

class Cycle(models.Model):
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True)
    scheme_name = models.ForeignKey(
        Scheme, on_delete=models.CASCADE, null=True, blank=True)
    cycle_no = models.CharField(max_length=255, blank=True, null=True)
    rounds = models.PositiveBigIntegerField(blank=True, null=True)
    cycle = models.CharField(
        max_length=50, choices=CYCLE, default='Months', blank=True)  
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    analytes = models.ManyToManyField(Analyte, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS, default='Inactive', blank=True)
    
    @property
    def noofanalytes(self):
        return self.analytes.count()

    def save(self, *args, **kwargs):
        # Skip status update if the instance is not yet saved (no ID)
        if self.pk is not None:
            if self.noofanalytes > 0:
                self.status = 'Active'
            else:
                self.status = 'Inactive'
        super(Cycle, self).save(*args, **kwargs)

    def __str__(self):
        return self.status

    class Meta:       
        verbose_name = 'Cycle'

class Sample(models.Model):
    organization_id = models.ForeignKey(
         Organization, on_delete=models.CASCADE, null=True, blank=True)
    account_id = models.OneToOneField(
        UserAccount, on_delete=models.CASCADE, primary_key=False, null=True, blank=True)
    sampleno = models.CharField(max_length=255, blank=False, null=True)
    details = models.TextField()
    notes = models.TextField(max_length=255, blank=False, null=True)
    scheme = models.TextField(blank=True, null=True) 
    # added_by = models.ForeignKey(
    #     UserAccount, on_delete=models.CASCADE, null=True, blank=True)
        
    def __str__(self):
        return self.sampleno

    class Meta:
        verbose_name = 'Sample'

class ActivityLogUnits(models.Model):
    added_by = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, verbose_name='added by', null=True)
    organization_id = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='databaseadmin_activity_log_units', null=True, blank=True)
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
    scheme_id = models.ForeignKey(
        Scheme, on_delete=models.CASCADE, null=True, blank=True)
    cycle_id = models.ForeignKey(
        Cycle, on_delete=models.CASCADE, null=True, blank=True)
    sample_id = models.ForeignKey(
        Sample, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    city_id = models.ForeignKey(
        City, on_delete=models.CASCADE, null=True, blank=True)
    country_id = models.ForeignKey(
        ParticipantCountry, on_delete=models.CASCADE, null=True, blank=True)
    province_id = models.ForeignKey(
        ParticipantProvince, on_delete=models.CASCADE, null=True, blank=True)
    district_id = models.ForeignKey(
        District, on_delete=models.CASCADE, null=True, blank=True)
    department_id = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True)
    designation_id = models.ForeignKey(
        Designation, on_delete=models.CASCADE, null=True, blank=True)
    type_id = models.ForeignKey(
        ParticipantType, on_delete=models.CASCADE, null=True, blank=True)
    sector_id = models.ForeignKey(
        ParticipantSector, on_delete=models.CASCADE, null=True, blank=True)
    old_value = models.TextField(null= True, blank=True)
    new_value = models.TextField(null= True, blank=True)
    date_of_addition = models.DateTimeField(blank=True, null=True)  
    date_of_updation = models.DateTimeField(blank=True, null=True, auto_now=True)
    field_name = models.CharField(max_length=255, null= True)
    actions = models.CharField(
        max_length=50, choices= ACTIONS, default= 'Added', verbose_name='Which action is performed?')
    status = models.CharField(
        max_length=50, choices=STATUS, default='Inactive', blank=True)
    cycle = models.CharField(
        max_length=50, choices=CYCLE, default='Months', blank=True)
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