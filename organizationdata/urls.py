# urls.py

from django.urls import path
from organizationdata.views import RegisterOrganizationView, OrganizationListView, OrganizationListUpdateAPIView, OrganizationListDeleteAPIView

urlpatterns = [
    path('register-organization', RegisterOrganizationView.as_view(), name='register-organization'),
    path('organization-list', OrganizationListView.as_view(), name='organization-list'),
    path('update-organization-list/<id>', OrganizationListUpdateAPIView.as_view(), name='update-organization-list/<id>'),
    path('delete-organization-list/<id>', OrganizationListDeleteAPIView.as_view(), name='delete-organization-list/<id>'),
]
