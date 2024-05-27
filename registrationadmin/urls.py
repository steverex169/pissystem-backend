from django.urls import path

from registrationadmin.views import  SharePercentageApprovedLabTestListView, LabListApprovedView, SharePercentageAllPendingLabTestView, SharePercentagePendingLabTestListView, UpdateReferrelLabTestListView, ApproveReferrelLabTestListView, ReferrelLabTestListView,  ApproveUnapproveLabView,  ApprovedLabsView, PendingLabsView,UnapprovedLabsView, LabListPendingView

urlpatterns = [
    # URLs for the labs
    path('pending-labs',
         PendingLabsView.as_view(), name='pending-labs'),
    path('approved-labs',
         ApprovedLabsView.as_view(), name='approved-labs'),
    path('unapproved-labs',
         UnapprovedLabsView.as_view(), name='unapproved-labs'),
    path('approve-unapprove-lab/<id>',
         ApproveUnapproveLabView.as_view(), name='approve-unapprove-lab'),

    path('referrel-fee-labhazir',
         ReferrelLabTestListView.as_view(), name='referrel-fee-labhazir'),
    path('approve-referrel-fee-labhazir',
         ApproveReferrelLabTestListView.as_view(), name='approve-referrel-fee-labhazir'),
    path('update-referrel-fee-labhazir/<id>',
         UpdateReferrelLabTestListView.as_view(), name='update-referrel-fee-labhazir'),
     path('lab-list-pending',
          LabListPendingView.as_view(), name='lab-list-pending'),
     path('lab-list-approved',
          LabListApprovedView.as_view(), name='lab-list-approved'),
     path('shared_percentage_pending_tests/<id>',
          SharePercentagePendingLabTestListView.as_view(), name='shared_percentage_pending_tests'),
     path('shared_percentage_Approved_tests/<id>',
          SharePercentageApprovedLabTestListView.as_view(), name='shared_percentage_pending_tests'),
     path('shared_percentage_all_pending_tests/<id>',
          SharePercentageAllPendingLabTestView.as_view(), name='shared_percentage_all_pending_tests'),

]
