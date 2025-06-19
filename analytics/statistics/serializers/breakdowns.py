from rest_framework import serializers


class CombinedBreakdownSerializer(serializers.Serializer):
    country = serializers.CharField()
    device = serializers.CharField()
    os = serializers.CharField()
    raw_clicks = serializers.IntegerField()
    unique_clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    earning = serializers.DecimalField(max_digits=10, decimal_places=2)


class DeviceBreakdownSerializer(serializers.Serializer):
    device = serializers.CharField()
    clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()


class OSBreakdownSerializer(serializers.Serializer):
    os = serializers.CharField()
    clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()
