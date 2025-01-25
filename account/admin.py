import imp
from django.contrib import admin
from account.models import UserAccount

from django.contrib import auth
from rest_framework.authtoken.models import TokenProxy
from django_rest_passwordreset.models import ResetPasswordToken


# Change settings for showing in Admin
class UserAccountAdmin(admin.ModelAdmin):
    readonly_fields = ('last_login', 'date_joined',  'last_login', 'password_foradmins')
    search_fields = ('username', 'last_login', 'account_type', 'last_login', 'password_foradmins')
    list_display = ('id', 'username', 'email', 'account_type',
                    'is_superuser', 'is_active', 'date_joined', 'last_login', 'password_foradmins')
    fields = ('username', 'account_type', 'is_superuser', 'last_login',
              'is_active', 'date_joined','password_foradmins')


# Register your models here
admin.site.register(UserAccount, UserAccountAdmin)

# Unregister not required models here
admin.site.unregister(auth.models.Group)
# admin.site.unregister(TokenProxy)
admin.site.unregister(ResetPasswordToken)
