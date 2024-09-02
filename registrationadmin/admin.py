from django.contrib import admin
from .models import Round, ActivityLogUnits,Payment, SelectedScheme, Statistics

# Register your models here.

class ActivityLogUnitsAdmin(admin.ModelAdmin):

    list_display = ('id', 'organization_id', 'round_id', 'issue_date', 'closing_date', 'old_value', 'new_value', 'date_of_addition', 'date_of_updation', 'field_name', 'actions', 'status')
    search_fields = ('id', 'organization_id', 'round_id', 'issue_date', 'closing_date', 'old_value', 'new_value', 'date_of_addition', 'date_of_updation', 'field_name', 'actions', 'status')

class RoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_id', 'rounds', 'scheme', 'cycle_no', 'sample', 'nooflabs', 'issue_date', 'closing_date', 'status')
    search_fields = ('id', 'organization_id', 'rounds', 'scheme', 'cycle_no', 'sample', 'nooflabs', 'issue_date', 'closing_date', 'status')

    def get_lab(self, obj):
        return ', '.join([lab.name for lab in obj.lab.all()])
    
# class SelectedSchemeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'organization_id', 'lab_id', 'scheme_id', 'added_at')
#     search_fields = ('id', 'organization_id', 'lab_id', 'scheme_id', 'added_at')

  

# class PaymentAdmin(admin.ModelAdmin):
#     list_display = (
#         'id', 'organization_id', 'participant_id','get_schemes',  'price',
#         'discount', 'photo', 'paymentmethod', 'paydate'
#     )
#     search_fields = (
#         'id', 'organization_id__name', 'participant_id__name','get_schemes', 
#         'price', 'discount', 'paymentmethod', 'paydate'
#     )
#     def get_schemes(self, obj):
#         return ', '.join([scheme.name for scheme in obj.scheme.all()])

#     get_schemes.short_description = 'Schemes'

class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'organization_id', 'participant_id', 'get_schemes', 'price',
        'discount', 'photo', 'paymentmethod', 'paydate'
    )
    search_fields = (
        'id', 'organization_id__name', 'participant_id__name', 'scheme', 
        'price', 'discount', 'paymentmethod', 'paydate'
    )

    def get_schemes(self, obj):
        if obj.scheme:
            scheme_ids = [int(sid) for sid in obj.scheme.split(',') if sid.isdigit()]
            schemes = SelectedScheme.objects.filter(id__in=scheme_ids)
            return ', '.join([scheme.id for scheme in schemes])
        return None

    get_schemes.short_description = 'Schemes'

class StatisticsAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_id', 'participant_id', 'scheme', 'analyte',  'mean_result', 'median_result', 'std_deviation', 'cv_percentage', 'robust_mean', 'rounds', 'result')
    search_fields = ('id', 'organization_id', 'participant_id', 'scheme', 'analyte','mean_result', 'median_result', 'std_deviation', 'cv_percentage', 'robust_mean', 'rounds', 'result')




admin.site.register(ActivityLogUnits, ActivityLogUnitsAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Statistics, StatisticsAdmin)
# admin.site.register(SelectedScheme, SelectedSchemeAdmin)
  
