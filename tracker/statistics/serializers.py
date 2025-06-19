from rest_framework import serializers
from tracker.models import Conversion


class ConversionSerializer(serializers.ModelSerializer):
    offer = serializers.CharField(source="offer.title", read_only=True)

    class Meta:
        model = Conversion
        fields = [
            "id",
            "created_at",
            "offer",
            "ip",
            "country",   # ✅ সরাসরি country পাঠাবে (no alias)
            "device",
            "status",
            "goal",
            "sub1",
            "sub2",
            "sub3",
            "sub4",
            "sub5",
            "payout"
        ]
