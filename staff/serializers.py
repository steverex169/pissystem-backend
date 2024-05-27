from rest_framework import serializers
from staff.models import Marketer, Staff


# Serializer for storing lab's information
class MarketerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketer
        fields = ('__all__')


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ('__all__')

