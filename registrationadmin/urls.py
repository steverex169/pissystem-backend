from django.urls import path
from registrationadmin.views import RoundAPIView, RoundPostAPIView, RoundUpdateAPIView,  ActivityLogRegistrationadmin

urlpatterns = [
    
    path('history_list/<id>', ActivityLogRegistrationadmin.as_view(), name='history_list'),
    path('round-list/<id>',
         RoundAPIView.as_view(), name='round-list/<id>'),
    path('post-round',
        RoundPostAPIView.as_view(), name='post-round'),
    path('update-round-list',
        RoundUpdateAPIView.as_view(), name='update-round-list'),    
]