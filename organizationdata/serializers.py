from rest_framework import serializers
from organizationdata.models import Organization, Scrapdata, ScrapBetwarVolumn, PartnerBetwarInfo, News


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
class PartnerBetwarInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerBetwarInfo
        fields = ('__all__')
class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ('__all__') 
