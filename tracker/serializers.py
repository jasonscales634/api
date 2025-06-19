#tracker\serializers.py
from rest_framework import serializers
from .models import Click, Conversion


class ClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = Click
        fields = [
            'id', 'created_at',
            'sub1', 'sub2', 'sub3', 'sub4', 'sub5',
            'ip', 'country', 'ua', 'city',
            'os', 'device',
            'device_time', 'ip_local_time',
            'revenue', 'payout',
            'offer', 'affiliate', 'affiliate_manager', 'host',
        ]
        read_only_fields = fields  # সব field read-only


class ConversionSerializer(serializers.ModelSerializer):
    transaction_id = serializers.SerializerMethodField()

    class Meta:
        model = Conversion
        fields = [
            'id', 'created_at', 'click_id', 'click_date',
            'sub1', 'sub2', 'sub3', 'sub4', 'sub5',
            'ip', 'country','city', 'ua', 'os', 'device',
            'device_time', 'ip_local_time',
            'goal_value', 'sum', 'status', 'comment',
            'transaction_id',
            'revenue', 'payout',
            'goal', 'currency', 'offer',
            'affiliate', 'affiliate_manager',
        ]
        read_only_fields = fields

    def get_transaction_id(self, obj):
        return obj.transaction_id or str(obj.id)
