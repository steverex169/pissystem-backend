from rest_framework import serializers
from databaseadmin.models import City

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('__all__')

