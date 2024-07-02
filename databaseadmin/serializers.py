from rest_framework import serializers
from databaseadmin.models import ParticipantSector,ParticipantType,Department,Designation,District,City,News,Instrument, Units, Analyte, ActivityLogUnits, Reagents, Manufactural, Method, InstrumentType


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('__all__')

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('__all__')
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ('__all__')

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ('__all__')

class ParticipantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantType
        fields = ('__all__')

class ParticipantSectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantSector
        fields = ('__all__')

class UnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Units
        fields = ('__all__')

class ReagentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reagents
        fields = ('__all__')

class ManufacturalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufactural
        fields = ('__all__')

class ActivityLogUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLogUnits
        fields = ('__all__')     

class InstrumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstrumentType
        fields = ('__all__')

class MethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Method
        fields = ('__all__')              

class AnalyteSerializer(serializers.ModelSerializer):
    noofreagents = serializers.IntegerField(read_only=True) 
    noofmethods = serializers.IntegerField(read_only=True) 
    noofinstruments = serializers.IntegerField(read_only=True) 
    master_unit_name = serializers.CharField(read_only=True)

    class Meta:
        model = Analyte
        fields = ('__all__') 

class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = ('__all__') 

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('__all__') 