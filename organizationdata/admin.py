from django.contrib import admin
from organizationdata.models import Organization, Scrapdata, ScrapBetwarVolumn, PartnerBetwarInfo, News


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'email',)
    search_fields = ('id', 'country', 'email',)
class PartnerBetwarInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'partner_name', 'volume_formula', 'partner_percentage',)
    search_fields = ('id', 'partner_name', 'volume_formula', 'partner_percentage',)
class ScraperdataAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'username', 'partner_name', 'partner', 'total', 'partner_profit', 'office_profit', 'website_url', 'password', 'figure', 'affiliate_profit', 'weekly' )
    search_fields = ('id', 'user', 'username', 'partner_name', 'partner')
class ScrapBetwarVolumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'partner_name', 'weak_date', 'volume')
    search_fields = ('id', 'partner_name', 'weak_date', 'volume')
class NewsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'date_of_addition', 'description',)
    search_fields = ('id', 'title', 'date_of_addition', 'description',)
# Register your models heres
admin.site.register(Scrapdata, ScraperdataAdmin)
admin.site.register(PartnerBetwarInfo, PartnerBetwarInfoAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(ScrapBetwarVolumn, ScrapBetwarVolumnAdmin)
admin.site.register(News, NewsAdmin)


# Register your models here.
