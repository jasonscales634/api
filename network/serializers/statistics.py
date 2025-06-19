# network/serializers/statistics.py

from rest_framework import serializers


class DailyStatSerializer(serializers.Serializer):
    date = serializers.DateField()
    clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()
    revenue = serializers.FloatField()
    payout = serializers.FloatField()


class OfferStatSerializer(serializers.Serializer):
    offer_id = serializers.IntegerField()
    offer_title = serializers.CharField()
    clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()
    revenue = serializers.FloatField()
    payout = serializers.FloatField()


class AffiliateStatSerializer(serializers.Serializer):
    affiliate_id = serializers.IntegerField()
    affiliate_name = serializers.CharField()
    clicks = serializers.IntegerField()
    conversions = serializers.IntegerField()
    revenue = serializers.FloatField()
    payout = serializers.FloatField()