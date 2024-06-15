from rest_framework import serializers
from registrationadmin.models import Round, ActivityLogUnits


class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = ('__all__')


class ActivityLogUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLogUnits
        fields = ('__all__')     