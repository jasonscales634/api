from rest_framework import serializers
from userpanel.models import OfferTrafficSource
from offer.models import Offer
from userpanel.serializers.offer import OfferListSerializer


class OfferTrafficSourceSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    offer_details = OfferListSerializer(source='offer', read_only=True)

    class Meta:
        model = OfferTrafficSource
        fields = [
            'id',
            'user',
            'offer',          # for POST/PUT
            'offer_details',  # for GET/display
            'source',
            'custom_info',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']