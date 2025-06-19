from rest_framework import serializers


class StatisticsSummarySerializer(serializers.Serializer):
    clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()
    earnings = serializers.DecimalField(max_digits=10, decimal_places=2)
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
