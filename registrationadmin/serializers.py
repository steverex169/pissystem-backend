from rest_framework import serializers
from registrationadmin.models import Round, ActivityLogUnits, Payment, SelectedScheme





class RoundSerializer(serializers.ModelSerializer):
    nooflabs = serializers.IntegerField(read_only=True)

    class Meta:
        model = Round
        fields = ('__all__') 
    
class ActivityLogUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLogUnits
        fields = ('__all__')     

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('__all__')     
class SelectedSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedScheme
        fields = ('__all__')     
