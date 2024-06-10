from django.urls import path
from organization.views import RegisterOrganizationView
urlpatterns = [
    path('register-organization/<id>',
        RegisterOrganizationView.as_view(), name='register-organization'),
]