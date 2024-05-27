from rest_framework import serializers
from accountstatement.models import CorporateLabStatement, AccountStatement, B2BAccountStatement, BankAccountStatement, DonorAccountStatement


class AccountStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountStatement
        fields = ('__all__')


class DonorAccountStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonorAccountStatement
        fields = ('__all__')

class B2BAccountStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = B2BAccountStatement
        fields = ('__all__')
class BankAccountStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccountStatement
        fields = ('__all__')

class CorporateLabStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorporateLabStatement
        fields = ('__all__')
