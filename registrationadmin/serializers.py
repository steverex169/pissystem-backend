from rest_framework import serializers
from .models import Round, ActivityLogUnits





class RoundSerializer(serializers.ModelSerializer):
    nooflabs = serializers.IntegerField(read_only=True)

    class Meta:
        model = Round
        fields = ('__all__') 

# class RoundSerializer(serializers.ModelSerializer):
#     nooflabs = serializers.IntegerField(read_only=True)
#     class Meta:
#         model = Round
#         fields = (
#             'id', 'account_id', 'organization_id', 'rounds', 'scheme', 'cycle_no', 'sample', 'participants',
#             'issue_date', 'closing_date', 'status', 'nooflabs'
#         )

#     def get_nooflabs(self, obj):
#         return obj.nooflabs        


class ActivityLogUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLogUnits
        fields = ('__all__')     
