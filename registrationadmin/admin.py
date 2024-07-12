from django.contrib import admin
from .models import Round, ActivityLogUnits,Payment

# Register your models here.

class ActivityLogUnitsAdmin(admin.ModelAdmin):

    list_display = ('id', 'organization_id', 'round_id', 'issue_date', 'closing_date', 'old_value', 'new_value', 'date_of_addition', 'date_of_updation', 'field_name', 'actions', 'status')
    search_fields = ('id', 'organization_id', 'round_id', 'issue_date', 'closing_date', 'old_value', 'new_value', 'date_of_addition', 'date_of_updation', 'field_name', 'actions', 'status')

class RoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_id', 'rounds', 'scheme', 'cycle_no', 'sample', 'nooflabs', 'issue_date', 'closing_date', 'status')
    search_fields = ('id', 'organization_id', 'rounds', 'scheme', 'cycle_no', 'sample', 'nooflabs', 'issue_date', 'closing_date', 'status')

    def get_lab(self, obj):
        return ', '.join([lab.name for lab in obj.lab.all()])

class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'organization_id', 'participant_id','get_schemes',  'price',
        'discount', 'photo', 'paymentmethod', 'paydate'
    )
    search_fields = (
        'id', 'organization_id__name', 'participant_id__name','get_schemes', 
        'price', 'discount', 'paymentmethod', 'paydate'
    )
    def get_schemes(self, obj):
        return ', '.join([scheme.name for scheme in obj.scheme.all()])

    get_schemes.short_description = 'Schemes'

admin.site.register(ActivityLogUnits, ActivityLogUnitsAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Payment, PaymentAdmin)
  
