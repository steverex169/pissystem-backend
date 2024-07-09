from django.contrib import admin
from databaseadmin.models import ParticipantProvince,ParticipantCountry,City,District,Department,Designation,ParticipantType,ParticipantSector,News,Instrument, Method,InstrumentType,ActivityLogUnits, Units, Reagents, Manufactural, Analyte

# Register your models here.

class ActivityLogUnitsAdmin(admin.ModelAdmin):
    list_display = ('id', 'reagent_id','method_id', 'analyte_id', 'instrumenttype_id','unit_id', "manufactural_id", 'type','old_value', 'new_value', 'date_of_addition','actions','status')
    search_fields = ('id', 'reagent_id','method_id', 'instrumenttype_id','unit_id', 'type','old_value', 'new_value', 'date_of_addition','actions','status')

class InstrumentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name', 'date_of_addition', )

class UnitsTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name', 'date_of_addition', )

class ManufacturalAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',  'website', 'country', 'date_of_addition' )
    search_fields = ('id', 'name',  'website', 'country', 'date_of_addition')

class MethodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'code','status')
    search_fields = ('id', 'name', 'date_of_addition', 'code','status')

class ReagentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'code','status')
    search_fields = ('id', 'name', 'date_of_addition', 'code','status')

class AnalyteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'code', 'get_methods','noofmethods', 'get_instruments','noofinstruments', 'get_reagents', 'noofreagents','get_units', 'master_unit','status')
    search_fields = ('id', 'name', 'date_of_addition', 'code', 'get_methods','noofmethods', 'get_instruments','noofinstruments', 'get_reagents', 'noofreagents','get_units', 'master_unit','status')

    def get_reagents(self, obj):
        return ', '.join([reagent.name for reagent in obj.reagents.all()])

    get_reagents.short_description = 'Reagents'

    def get_instruments(self, obj):
        return ', '.join([instrument.name for instrument in obj.instruments.all()])

    get_instruments.short_description = 'Instruments'

    def get_methods(self, obj):
        return ', '.join([methods.name for methods in obj.methods.all()])

    get_methods.short_description = 'Methods'

    def get_units(self, obj):
        return ', '.join([units.name for units in obj.units.all()])

    get_units.short_description = 'Units'

class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', 'code','status','manufactural','instrument_type')
    search_fields = ('id', 'name', 'date_of_addition', 'code','status','manufactural','instrument_type')

class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date_of_addition', 'description',)
    search_fields = ('id', 'title', 'date_of_addition', 'description',)

class CityTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name','date_of_addition', )

class CountryTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name','date_of_addition', )

class ProvinceTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name','date_of_addition', )

class DistrictTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name','date_of_addition', )

class DepartmentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name','date_of_addition', )

class DesignationTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name','date_of_addition', )

class ParticipantTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name','date_of_addition', )

class ParticipantSectorTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name','date_of_addition', )

admin.site.register(Analyte, AnalyteAdmin) 
admin.site.register(Manufactural, ManufacturalAdmin)
admin.site.register(Reagents, ReagentsAdmin)
admin.site.register(Units, UnitsTypeAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(InstrumentType, InstrumentTypeAdmin)
admin.site.register(ActivityLogUnits, ActivityLogUnitsAdmin)
admin.site.register(Method, MethodAdmin)
admin.site.register(Instrument, InstrumentAdmin)
admin.site.register(City, CityTypeAdmin)
admin.site.register(ParticipantCountry, CountryTypeAdmin)
admin.site.register(ParticipantProvince, ProvinceTypeAdmin)
admin.site.register(District, DistrictTypeAdmin)
admin.site.register(Department, DepartmentTypeAdmin)
admin.site.register(Designation, DesignationTypeAdmin)
admin.site.register(ParticipantType, ParticipantTypeAdmin)
admin.site.register(ParticipantSector, ParticipantSectorTypeAdmin)
