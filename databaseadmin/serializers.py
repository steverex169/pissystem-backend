from rest_framework import serializers
from databaseadmin.models import News,Instrument, Units, Analyte, ActivityLogUnits, Reagents, Manufactural, Method, InstrumentType


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
    class Meta:
        model = Analyte
        fields = '__all__'
        extra_kwargs = {
            'reagents': {'required': False},
        }

class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = ('__all__') 

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('__all__') 