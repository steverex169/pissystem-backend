from django.contrib import admin

from staff.models import Marketer, Staff


# Register your models here.
class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cnic', 'email','photo',
                    'phone', 'staff_type','city')
    search_fields = ('name', 'cnic', 'photo', 'email', 'phone', 'staff_type', )


class Marketerdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'cnic', 'email', 'phone', 'city', 'count',
                    'total_count', 'registered_at', 'last_paid_at')
    search_fields = ('name', 'cnic', 'email', 'phone', 'city', 'count',
                     'total_count', 'registered_at', 'last_paid_at')


admin.site.register(Staff, StaffAdmin)
admin.site.register(Marketer, Marketerdmin)
