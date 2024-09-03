from rest_framework import serializers
from labowner.models import LabCorporate, Result, Lab, LabPayment, ActivityLog, OfferedTest, Pathologist, SampleCollector



# Serializer for storing lab's information
class LabInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lab
        fields = ('__all__')


class OfferedTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferedTest
        fields = ('__all__')


class PathologistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pathologist
        fields = ('__all__')


class SampleCollectorSerializer(serializers.ModelSerializer):

    class Meta:
        model = SampleCollector
        fields = ('__all__')


class ResultSerializer(serializers.ModelSerializer):
    lab = LabInformationSerializer(source='lab_id', read_only=True)
    class Meta:
        model = Result
        fields = ('__all__') 


class LabPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabPayment
        fields = ('__all__')

class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog       
        fields = ('__all__')
        
class LabCorporateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabCorporate       
        fields = ('__all__')
        
# class ManufacturalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Manufactural
#         fields = ('__all__')