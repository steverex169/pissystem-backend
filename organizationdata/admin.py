from django.contrib import admin
from organizationdata.models import Organization, Scrapdata


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'email',)
    search_fields = ('id', 'country', 'email',)
class ScraperdataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'username', 'partner_name', 'partner', 'partner_percentage')
    search_fields = ('id', 'user', 'username', 'partner_name', 'partner', 'partner_percentage')

# Register your models here
admin.site.register(Scrapdata, ScraperdataAdmin)
admin.site.register(Organization, OrganizationAdmin)

# Register your models here.
