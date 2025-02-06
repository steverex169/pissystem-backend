from rest_framework import serializers
from organizationdata.models import Organization, Scrapdata, ScrapBetwarVolumn


# Serializer for storing lab's information
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('__all__')
class ScrapdataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrapdata
        fields = ('__all__')

class ScrapBetwarVolumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapBetwarVolumn
        fields = ('__all__')