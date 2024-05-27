from django.urls import path

from accountstatement.views import  AccountStatementsView

urlpatterns = [
    path('lab-account-statements/<id>',
         AccountStatementsView.as_view(), name='lab-account-statements'),

]

