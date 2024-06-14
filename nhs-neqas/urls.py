"""nhs-neqas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from account.views import redirect_to_admin_view

admin.site.site_header = "nhs-neqas"
admin.site.site_title = "nhs-neqas Admin Portal"
admin.site.index_title = "Welcome to nhs-neqas"

urlpatterns = [
    path('', redirect_to_admin_view),
    path('admin/', admin.site.urls),
    path('api/account/', include('account.urls')),
    path('api/lab/', include('labowner.urls')),
    path('api/staff/', include('staff.urls')),
    path('api/accountstatement/', include('accountstatement.urls')),
    path('api/registration-admin/', include('registrationadmin.urls')),
    path('api/database-admin/', include('databaseadmin.urls')),
    path('api/finance-officer/', include('financeofficer.urls')),
    path('api/hr-admin/', include('hradmin.urls')),
    path('api/database-admin/', include('databaseadmin.urls')),
    path('api/territories/', include('territories.urls')),
    path('api/organization/', include('organization.urls')),
    path('api/superadmin/', include('superadmin.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
