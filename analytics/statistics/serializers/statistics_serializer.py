from rest_framework import serializers
from analytics.statistics.models.statistics import DailyStat

class DailyStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyStat
        fields = '__all__'
