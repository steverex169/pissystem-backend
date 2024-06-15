from django.contrib import admin
from databaseadmin.models import News,Instrument, Method, Scheme, Sample, InstrumentType,ActivityLogUnits, Units, Reagents, Manufactural, Analyte

# Register your models here.

class ActivityLogUnitsAdmin(admin.ModelAdmin):

    list_display = ('id', 'organization_id', 'reagent_id','method_id', 'scheme_id', 'sample_id',  'start_date', 'end_date', 'analyte_id', 'instrumenttype_id','unit_id', 'manufactural_id', 'type','old_value', 'new_value', 'date_of_addition','actions','status', 'cycle')
    search_fields = ('id', 'organization_id', 'reagent_id','method_id',  'scheme_id', 'sample_id',  'start_date', 'end_date','analyte_id', 'instrumenttype_id','unit_id', 'manufactural_id', 'type','old_value', 'new_value', 'date_of_addition','actions','status', 'cycle')

class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name', 'date_of_addition', )

class UnitsTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name', 'date_of_addition', )

class ManufacturalAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'telephone', 'city', 'country', 'address', 'date_of_addition', )
    search_fields = ('id', 'name','telephone', 'city', 'country', 'address',  'date_of_addition', )

class MethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition','code','status')
    search_fields = ('id', 'name', 'date_of_addition','code','status')

class SchemeAdmin(admin.ModelAdmin):
    list_display = ('id', 'organization_id', 'scheme_name', 'cycle_no', 'rounds','cycle', 'start_date', 'end_date', 'status')
    search_fields = ('id', 'organization_id', 'scheme_name', 'cycle_no', 'rounds','cycle', 'start_date', 'end_date', 'status')

class ReagentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'code','status')
    search_fields = ('id', 'name', 'date_of_addition', 'code','status')

class AnalyteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'code','status')
    search_fields = ('id', 'name', 'date_of_addition', 'code','status')
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'code','status','manufactural','instrument_type')
    search_fields = ('id', 'name', 'date_of_addition', 'code','status','manufactural','instrument_type')
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date_of_addition', 'description',)
    search_fields = ('id', 'title', 'date_of_addition', 'description',)

class SampleAdmin(admin.ModelAdmin):
    list_display = ('id', 'sampleno', 'details', 'notes','scheme')
    search_fields = ('id', 'sampleno', 'details', 'notes','scheme')
    
admin.site.register(Analyte, AnalyteAdmin) 
admin.site.register(Manufactural, ManufacturalAdmin)
admin.site.register(Reagents, ReagentsAdmin)
admin.site.register(Units, UnitsTypeAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(InstrumentType, InstrumentTypeAdmin)
admin.site.register(ActivityLogUnits, ActivityLogUnitsAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(Scheme, SchemeAdmin)
admin.site.register(Instrument, InstrumentAdmin)
admin.site.register(Sample, SampleAdmin)
