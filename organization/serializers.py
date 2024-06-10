from rest_framework import serializers
from organization.models import Organization


# Serializer for storing lab's information
class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ('__all__')
