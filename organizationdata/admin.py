from django.contrib import admin
from organizationdata.models import Organization


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'country', 'website','registered_at',)
    search_fields = ('id', 'name', 'country', 'email', 'website', 'registered_at',)

# Register your models here
admin.site.register(Organization, OrganizationAdmin)
from django.contrib import admin

# Register your models here.
