from django.urls import path

from financeofficer.views import  InvoiceAdjustmentView,   BankTransferDetailView, PaymentOutnClearedListView, PaymentInView, PaymentInBouncedListView, PaymentOutBouncedListView, PaymentOutCreatedListView, PaymentOutPendingListView, PaymentOutView, PaymentInCreatedListView, PaymentInDepositedListView, PaymentInClearedListView, LabMOFListView

urlpatterns = [

    path('payment-in/<id>',
         PaymentInView.as_view(), name='payment-in'),
    path('payment-out/<id>',
         PaymentOutView.as_view(), name='payment-out'),
    path('get-payment-in-created/<id>',
         PaymentInCreatedListView.as_view(), name='get-payment-in-created'),
    path('get-payment-in-deposited/<id>',
         PaymentInDepositedListView.as_view(), name='get-payment-in-deposited'),
    path('get-payment-in-cleared/<id>',
         PaymentInClearedListView.as_view(), name='get-payment-in-cleared'),
    path('get-payment-out-created/<id>',
         PaymentOutCreatedListView.as_view(), name='get-payment-out-created'),
    path('get-payment-in-bounced/<id>',
          PaymentInBouncedListView.as_view(), name='get-payment-in-bounced'),
    path('get-payment-out-pending/<id>',
         PaymentOutPendingListView.as_view(), name='get-payment-out-pending'),
    path('get-payment-out-created/<id>',
          PaymentOutCreatedListView.as_view(), name='get-payment-out-created'),
    path('get-payment-out-bounced/<id>',
          PaymentOutBouncedListView.as_view(), name='get-payment-out-bounced'),
    path('get-payment-out-created/<id>',
         PaymentOutCreatedListView.as_view(), name='get-payment-out-created'),
    path('lab-MOF-list',
         LabMOFListView.as_view(), name='lab-MOF-list'),
    path('get-payment-out-cleared/<id>',
         PaymentOutnClearedListView.as_view(), name='get-payment-out-cleared'),

    path('bank-transfer-detail/<id>',
        BankTransferDetailView.as_view(), name='Bank-Transfer-Detail'),
    path('invoice-adjustment-detail/<id>',
        InvoiceAdjustmentView.as_view(), name='invoice-adjustment-detail'),


]
