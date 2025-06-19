# analytics/statistics/serializers/clicks.py

from rest_framework import serializers
from analytics.statistics.serializers.clicks import ClickSerializer

class ClickOfferSerializer(serializers.Serializer):
    id = serializers.CharField()
    offer_id = serializers.CharField()
    title = serializers.CharField()

class ClickSerializer(serializers.Serializer):
    id = serializers.CharField()
    ip = serializers.CharField()
    ua = serializers.CharField()
    country = serializers.CharField()
    city = serializers.CharField(allow_blank=True)
    device = serializers.CharField()
    os = serializers.CharField()
    browser = serializers.CharField()
    referrer = serializers.CharField(allow_blank=True)
    sub1 = serializers.CharField(allow_blank=True)
    sub2 = serializers.CharField(allow_blank=True)
    sub3 = serializers.CharField(allow_blank=True)
    sub4 = serializers.CharField(allow_blank=True)
    sub5 = serializers.CharField(allow_blank=True)
    offer = ClickOfferSerializer()
    conversion_id = serializers.CharField(allow_blank=True)
    ios_idfa = serializers.CharField(allow_blank=True)
    android_id = serializers.CharField(allow_blank=True)
    created_at = serializers.CharField()
    uniq = serializers.IntegerField()
    cbid = serializers.CharField()
    partner_id = serializers.IntegerField()
