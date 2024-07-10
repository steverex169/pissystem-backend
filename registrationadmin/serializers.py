from rest_framework import serializers
from registrationadmin.models import Round, ActivityLogUnits


class RoundSerializer(serializers.ModelSerializer):
    nooflabs = serializers.SerializerMethodField()
    class Meta:
        model = Round
        fields = ('__all__')

    def get_nooflabs(self, obj):
        return obj.nooflabs        


class ActivityLogUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLogUnits
        fields = ('__all__')     