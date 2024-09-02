from rest_framework import serializers
from databaseadmin.models import Analyte, Scheme
from registrationadmin.models import Round, ActivityLogUnits, SelectedScheme, Payment, Statistics

class RoundSerializer(serializers.ModelSerializer):
    nooflabs = serializers.IntegerField(read_only=True)
    issue_date = serializers.SerializerMethodField()
    closing_date = serializers.SerializerMethodField()

    class Meta:
        model = Round
        fields = ('__all__') 
        
    def get_issue_date(self, obj):
       return obj.issue_date.date() if obj.issue_date else None

    def get_closing_date(self, obj):
        return obj.closing_date.date() if obj.closing_date else None
    
class ActivityLogUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLogUnits
        fields = ('__all__')     
        
class SelectedSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectedScheme
        fields = '__all__'
        
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('__all__')   
  
class AnalyteSchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analyte
        fields = ('__all__')

# //////////Statistics  
class StatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistics
        fields = '__all__'
     
# class ZScoreWithLabSerializer(serializers.Serializer):
#     lab_id = serializers.IntegerField()
#     z_score = serializers.FloatField()

# class StatisticsSerializer(serializers.ModelSerializer):
#     z_scores_with_lab = ZScoreWithLabSerializer(many=True)

# class Meta:
#     model = Statistics
#     fields = ('__all__')  
# //////////Statistics 

# class ZScoreWithLabSerializer(serializers.Serializer):
#     lab_id = serializers.IntegerField()
#     z_score = serializers.FloatField()
# class AnalyteResultSubmitSerializer(serializers.Serializer):
#     analyte_id = serializers.IntegerField()
#     analyte_name = serializers.CharField(max_length=255)
#     lab_count = serializers.IntegerField()
#     mean_result = serializers.FloatField()
#     median_result = serializers.FloatField()
#     std_deviation = serializers.FloatField()
#     cv_percentage = serializers.FloatField()
#     uncertainty = serializers.FloatField()
#     robust_mean = serializers.FloatField()
#     z_scores_with_lab = ZScoreWithLabSerializer(many=True)