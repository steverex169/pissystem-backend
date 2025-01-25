from rest_framework import serializers
from organizationdata.models import Organization, Scrapdata


# Serializer for storing lab's information
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('__all__')
class ScrapdataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrapdata
        fields = ('__all__')