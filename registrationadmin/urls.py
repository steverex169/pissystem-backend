from django.urls import path
from registrationadmin.views import ParticipantResultView, PaymentPostAPIView, RoundAPIView,ApproveUnapproveLabView,  RoundPostAPIView, RoundUpdateAPIView, RoundDeleteAPIView,  ActivityLogRegistrationadmin, PendingLabsView, ApprovedLabsView, UnapprovedLabsView, RoundsLabsAPIView, RoundAddLabsAPIView, RoundUpdateLabsAPIView, SelectedSchemeListAPIView, SelectedSchemeAnalytesList,AnalyteSpecificScheme


urlpatterns = [
    path('pending-labs/<id>',
         PendingLabsView.as_view(), name='pending-labs/<id>'),
    path('approved-labs/<id>',
         ApprovedLabsView.as_view(), name='approved-labs/<id>'),
    path('unapproved-labs/<id>',
         UnapprovedLabsView.as_view(), name='unapproved-labs/<id>'),
    path('approve-unapprove-lab/<id>',
         ApproveUnapproveLabView.as_view(), name='approve-unapprove-lab'),
    path('history_list/<id>', ActivityLogRegistrationadmin.as_view(), name='history_list'),
    path('round-list/<id>',
         RoundAPIView.as_view(), name='round-list/<id>'),
    path('post-round',
        RoundPostAPIView.as_view(), name='post-round'),
    path('update-round-list/<id>',
        RoundUpdateAPIView.as_view(), name='update-round-list/<id>+'), 
    path('delete-round/<id>',
        RoundDeleteAPIView.as_view(), name='delete-round/<id>'),

     # Rounds Adding Labs
    path('round-labs-list/<id>',
         RoundsLabsAPIView.as_view(), name='round-labs-list'),     
    path('round-add-lab/<id>',
        RoundAddLabsAPIView.as_view(), name='round-add-lab'),
    path('round-update-lab/<id>',
         RoundUpdateLabsAPIView.as_view(), name='round-update-lab'),

     # selected-schemes related to participants
    path('selectedSchemes-list/<id>',
         SelectedSchemeListAPIView.as_view(), name='selectedSchemes-list'), 
    path('selectedSchemesAnalytes-list/<id>',
         SelectedSchemeAnalytesList.as_view(), name='selectedSchemesAnalytes-list'), 

    path('analyteSpecificScheme-list/<id>',
         AnalyteSpecificScheme.as_view(), name='analyteSpecificScheme-list'), 
     # Participant Result page    
    path('resultpost/<id>',
         ParticipantResultView.as_view(), name='resultpost'), 
    path('getResultsData/<id>',
         ParticipantResultView.as_view(), name='getResultsData'), 
     
     #adding payment
     path('add-payment',
         PaymentPostAPIView.as_view(), name='add-payment'),
     
]
