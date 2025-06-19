from rest_framework import serializers
from analytics.statistics.models.country import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['code', 'name']


class CountryBreakdownSerializer(serializers.Serializer):
    country = serializers.CharField()
    raw_clicks = serializers.IntegerField()
    unique_clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    earning = serializers.DecimalField(max_digits=10, decimal_places=2)
