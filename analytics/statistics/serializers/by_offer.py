from rest_framework import serializers

class OfferBreakdownSerializer(serializers.Serializer):
    offer_id = serializers.CharField()
    offer_title = serializers.CharField()
    raw_clicks = serializers.IntegerField()
    unique_clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    earning = serializers.DecimalField(max_digits=10, decimal_places=2)
