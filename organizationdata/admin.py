from django.contrib import admin
from organizationdata.models import Organization, Scrapdata, ScrapBetwarVolumn


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'email',)
    search_fields = ('id', 'country', 'email',)
class ScraperdataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'username', 'partner_name', 'partner', 'partner_percentage', 'total', 'partner_profit', 'office_profit', 'website_url', 'password', 'figure', 'affiliate_profit', 'weekly' )
    search_fields = ('id', 'user', 'username', 'partner_name', 'partner', 'partner_percentage')
class ScrapBetwarVolumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'partner_name', 'weak_date', 'volume')
    search_fields = ('id', 'partner_name', 'weak_date', 'volume')
# Register your models here
admin.site.register(Scrapdata, ScraperdataAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(ScrapBetwarVolumn, ScrapBetwarVolumnAdmin)


# Register your models here.
