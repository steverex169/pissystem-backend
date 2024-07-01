from django.contrib import admin
from registrationadmin.models import Round, ActivityLogUnits

# Register your models here.

class ActivityLogUnitsAdmin(admin.ModelAdmin):

    list_display = ('id', 'organization_id', 'round_id', 'issue_date', 'closing_date', 'old_value', 'new_value', 'date_of_addition', 'date_of_updation', 'field_name', 'actions', 'status')
    search_fields = ('id', 'organization_id', 'round_id', 'issue_date', 'closing_date', 'old_value', 'new_value', 'date_of_addition', 'date_of_updation', 'field_name', 'actions', 'status')

class RoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_id', 'rounds', 'scheme',  'cycle_no', 'sample', 'issue_date', 'closing_date', 'notes', 'status')
    search_fields = ('id', 'organization_id', 'rounds', 'scheme',  'cycle_no', 'sample', 'issue_date', 'closing_date', 'notes', 'status')
    

admin.site.register(ActivityLogUnits, ActivityLogUnitsAdmin)
admin.site.register(Round, RoundAdmin)

