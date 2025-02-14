from django.contrib import admin
from databaseadmin.models import City


    
class CityTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'date_of_addition', )
    search_fields = ('id', 'name','date_of_addition', )



admin.site.register(City, CityTypeAdmin)
