from rest_framework import serializers
from analytics.statistics.models.clicks import Click

class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Click
        fields = '__all__'
