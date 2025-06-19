from rest_framework import serializers
from analytics.statistics.models.country import Country

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '_all_'