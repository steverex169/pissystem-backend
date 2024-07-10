from django.urls import path
from registrationadmin.views import AllLabsView, RoundAPIView,ApproveUnapproveLabView,  RoundPostAPIView, RoundUpdateAPIView, RoundDeleteAPIView,  ActivityLogRegistrationadmin, PendingLabsView, ApprovedLabsView, UnapprovedLabsView


urlpatterns = [
    path('pending-labs/<id>',
         PendingLabsView.as_view(), name='pending-labs/<id>'),
     path('all-labs/<id>',
         AllLabsView.as_view(), name='all-labs/<id>'),
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
]
