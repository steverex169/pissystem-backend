from django.urls import path

from staff.views import FinanceOfficerListView,OrganizationListView,  CSRAdminAppointmentListView, CommentsListView, CSRAppointmentListView, CSRNorthListView, CSRSouthListView, CSRCentralListView,AuditorListView, CSRListView, RegisterStaffView, StaffProfileView, AuditorCentralListView, AuditorSouthListView, AuditorNorthListView


urlpatterns = [
    path('csr-list/<id>', CSRListView.as_view(),
         name='csr-list/<id>'),
     path('csr-central-list', CSRCentralListView.as_view(),
         name='csr-central-list'),
     path('csr-south-list', CSRSouthListView.as_view(),
         name='csr-south-list'),
     path('csr-north-list', CSRNorthListView.as_view(),
         name='csr-north-list'),
     path('organization-list', OrganizationListView.as_view(),
         name='organization-list'),
    path('auditor-list/<id>', AuditorListView.as_view(),
         name='auditor-list/<id>'),
     path('auditor-central-list', AuditorCentralListView.as_view(),
         name='auditor-central-list'),
     path('auditor-south-list', AuditorSouthListView.as_view(),
         name='auditor-south-list'),
     path('auditor-north-list', AuditorNorthListView.as_view(),
         name='auditor-north-list'),
    path('finance-officer-list/<id>', FinanceOfficerListView.as_view(),
         name='finance-officer-list/<id>'),
    path('register-staff/<id>',
         RegisterStaffView.as_view(), name='register-staff'),
    path('staff-profile/<account_id>',
         StaffProfileView.as_view(), name='staff-profile'),
    path('csr-appointment/<id>',
         CSRAppointmentListView.as_view(), name='csr-appointment'),
    path('csr-admin-appointment/<id>',
         CSRAdminAppointmentListView.as_view(), name='csr-admin-appointment'),
    path('add-note/<id>',
         CommentsListView.as_view(), name='add-note'),
]
