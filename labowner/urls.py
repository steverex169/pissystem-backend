from django.urls import path

from labowner.views import  ParticipentResultView, ForChartCalculationView, LabNamesView, OfferedRadiologyShareListView, OfferedPackageShareListView, OfferedProfileShareListView, QualityCertificateCollectionPointView, ActivityLogView, OfferedTestCollectionPointView, OfferedTestDiscountListView, OfferedTestShareListView, LabInformationView, FeedbackListView, LabListView, LabProfileView, LabSettingsView, OfferedTestListView, OfferedTestView, PathologistListView, PathologistView, TestAppointmentCompletedListView, TestAppointmentInProcessListView, discountAllOfferedTestView, discountOfferedTestListView, LabPaymentView, LabListByOrganization

urlpatterns = [

    path('participant-information/<id>', LabListByOrganization.as_view(), name='participant-information'),
    path('lab-names/',
         LabNamesView.as_view(), name='lab-names/'),
    path('lab-information/<account_id>',
         LabInformationView.as_view(), name='lab-information'),
    path('lab-profile/<account_id>',
         LabProfileView.as_view(), name='lab-profile'),
    path('lab-settings/<id>',
         LabSettingsView.as_view(), name='lab-settings'),
    path('lab-list', LabListView.as_view(), name='lab-list'),

    path('offered-test/<id>', OfferedTestView.as_view(), name='offered-test'),
    path('offered-test-share-list/<id>', OfferedTestShareListView.as_view(), name='offered-test-share-list'),
    path('offered-profile-share-list/<id>', OfferedProfileShareListView.as_view(), name='offered-profile-share-list'),
    path('offered-package-share-list/<id>', OfferedPackageShareListView.as_view(), name='offered-package-share-list'),
    path('offered-radiology-share-list/<id>', OfferedRadiologyShareListView.as_view(), name='offered-radiology-share-list'),
    path('offered-test-list/<id>',
         OfferedTestListView.as_view(), name='offered-test-list'),
    path('offered-test-main-lab/<id>', OfferedTestCollectionPointView.as_view(), name='offered-test-main-lab'),
    path('offered-test-discount-list/<id>',
         OfferedTestDiscountListView.as_view(), name='offered-test-discount-list'),

    path('pathologist/<id>',
         PathologistView.as_view(), name='pathologist'),
    path('pathologist-list/<user_id>',
         PathologistListView.as_view(), name='pathologist-list'),


#     path('quality-certificate-list/<user_id>',
#          QualityCertificateListView.as_view(), name='quality-certificate-list'),
#     path('quality-certificate/<id>',
#          QualityCertificateView.as_view(), name='quality-certificate'),
    path('feedback-list/<id>',
         FeedbackListView.as_view(), name='feedback-list'),



    path('quality-certificate-collectionpoint-list/<id>',
         QualityCertificateCollectionPointView.as_view(), name='quality-certificate-collectionpoint-list'),

    path('test-appointment-completed-list/<id>',
         TestAppointmentCompletedListView.as_view(), name='test-appointment-completed-list'),
    path('test-appointment-in-process-list/<id>',
         TestAppointmentInProcessListView.as_view(), name='test-appointment-in-process-list'),

     path('discount-offered-test/<id>',
        discountOfferedTestListView.as_view(), name='discount-offered-test'),
     path('discount-all-offered-tests/<id>',
        discountAllOfferedTestView.as_view(), name='discount-all-offered-tests'),     
     path('lab-payment/<id>',
         LabPaymentView.as_view(), name='lab-payment'),

    path('activity-log/<id>', ActivityLogView.as_view(), name='activity-log'),
#     path('manufactural-list', ManufacturalList.as_view(), name='manufactural-list'),
    path('ForChartCalculation', ForChartCalculationView.as_view(), name='ForChartCalculation'),
    path('PaticipentResult/<id>', ParticipentResultView.as_view(), name='PaticipentResult'),

]
