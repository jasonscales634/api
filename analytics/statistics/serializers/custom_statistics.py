from rest_framework import serializers

class CustomStatisticsSerializer(serializers.Serializer):
    date = serializers.DateField()
    impressions = serializers.IntegerField()
    clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()
    revenue = serializers.FloatField()
    payout = serializers.FloatField()
    epc = serializers.FloatField()
    cr = serializers.FloatField()