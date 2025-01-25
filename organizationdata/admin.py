from django.contrib import admin
from organizationdata.models import Organization, Scrapdata


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'email',)
    search_fields = ('id', 'country', 'email',)
class ScraperdataAdmin(admin.ModelAdmin):
    list_display = ('id', 'partner_name', 'partner')
    search_fields = ('id', 'partner_name', 'partner')

# Register your models here
admin.site.register(Scrapdata, ScraperdataAdmin)
admin.site.register(Organization, OrganizationAdmin)
from django.contrib import admin

# Register your models here.
