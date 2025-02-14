from rest_framework import serializers

class DropdownDataSerializer(serializers.Serializer):
    website_url = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    figure = serializers.CharField()
    affiliate_profit = serializers.CharField()
    office_profit = serializers.CharField()

class PartnerDataSerializer(serializers.Serializer):
    partner_name = serializers.CharField()
    total = serializers.CharField()
    partner_profit = serializers.CharField()
    office_profit = serializers.CharField()
    dropdown_data = DropdownDataSerializer(many=True)
