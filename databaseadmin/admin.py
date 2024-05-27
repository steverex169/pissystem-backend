from django.contrib import admin
from databaseadmin.models import News,Instrument, Method,InstrumentType,ActivityLogUnits, Units, Reagents, Manufactural, Analyte

# Register your models here.

class ActivityLogUnitsAdmin(admin.ModelAdmin):
    list_display = ('id', 'reagent_id','method_id', 'analyte_id', 'instrumenttype_id','unit_id', "manufactural_id", 'type','old_value', 'new_value', 'date_of_addition','added_by','actions','status')
    search_fields = ('id', 'reagent_id','method_id', 'instrumenttype_id','unit_id', 'type','old_value', 'new_value', 'date_of_addition','added_by','actions','status')

class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'added_by')
    search_fields = ('id', 'name', 'date_of_addition', 'added_by')

class UnitsTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'added_by')
    search_fields = ('id', 'name', 'date_of_addition', 'added_by')

class ManufacturalAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'telephone', 'city', 'country', 'address', 'date_of_addition', 'added_by')
    search_fields = ('id', 'name','telephone', 'city', 'country', 'address',  'date_of_addition', 'added_by')

class MethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'added_by','code','status')
    search_fields = ('id', 'name', 'date_of_addition', 'added_by','code','status')

class ReagentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'added_by','code','status')
    search_fields = ('id', 'name', 'date_of_addition', 'added_by','code','status')

class AnalyteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'added_by','code','status')
    search_fields = ('id', 'name', 'date_of_addition', 'added_by','code','status')
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'added_by','code','status','manufactural','instrument_type')
    search_fields = ('id', 'name', 'date_of_addition', 'added_by','code','status','manufactural','instrument_type')
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date_of_addition', 'added_by','description','picture')
    search_fields = ('id', 'title', 'date_of_addition', 'added_by','description','picture')
admin.site.register(Analyte, AnalyteAdmin) 
admin.site.register(Manufactural, ManufacturalAdmin)
admin.site.register(Reagents, ReagentsAdmin)
admin.site.register(Units, UnitsTypeAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(InstrumentType, InstrumentTypeAdmin)
admin.site.register(ActivityLogUnits, ActivityLogUnitsAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(Instrument, InstrumentAdmin)
