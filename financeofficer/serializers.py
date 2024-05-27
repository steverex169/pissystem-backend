from rest_framework import serializers
from financeofficer.models import PaymentIn, PaymentOut, BankTransferDetail, ActivityLogFinance, InvoiceAdjustment



class PaymentInSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentIn
        fields = ('__all__')

class PaymentOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentOut
        fields = ('__all__')
class BankTransferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankTransferDetail
        fields = ('__all__')
class InvoiceAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceAdjustment
        fields = ('__all__')
class ActivityLogFinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLogFinance
        fields = ('__all__')