from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from territories.models import Territories


# Change settings for showing in Admin
class TerritoriesAdmin(admin.ModelAdmin):
    search_fields = ('id', 'province','city', 'district', 'office',
                     )
    list_display = ('id', 'province','city', 'district', 'office',
                     )


# Register your models here
admin.site.register(Territories, TerritoriesAdmin)

