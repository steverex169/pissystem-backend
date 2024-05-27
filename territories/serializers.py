from rest_framework import serializers
from territories.models import Territories


# serializer of the territorieslist
class TerritoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Territories
        fields = ('__all__')


