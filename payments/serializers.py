from rest_framework import serializers
from .models import Payment, StatusLog, PaymentStatusLog

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at']

    def validate(self, data):
        method = data.get('method')

        if method == 'bank':
            if not data.get('account_number'):
                raise serializers.ValidationError({"account_number": "Required for bank transfers."})
            if not data.get('bank_name'):
                raise serializers.ValidationError({"bank_name": "Bank name is required for bank transfers."})

        elif method == 'paypal':
            if not data.get('payment_email'):
                raise serializers.ValidationError({"payment_email": "PayPal email is required."})

        elif method == 'crypto':
            if not data.get('wallet_address'):
                raise serializers.ValidationError({"wallet_address": "Wallet address is required for crypto."})
            if not data.get('crypto_network'):
                raise serializers.ValidationError({"crypto_network": "Crypto network (e.g. TRC20) is required."})

        return data


class PaymentDetailSerializer(serializers.ModelSerializer):
    logs = serializers.SerializerMethodField()
    status_logs = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = '__all__'

    def get_logs(self, obj):
        return StatusLogSerializer(obj.logs.all(), many=True).data

    def get_status_logs(self, obj):
        return PaymentStatusLogSerializer(obj.status_logs.all(), many=True).data


class StatusLogSerializer(serializers.ModelSerializer):
    updated_by = serializers.StringRelatedField()

    class Meta:
        model = StatusLog
        fields = '__all__'


class PaymentStatusLogSerializer(serializers.ModelSerializer):
    changed_by = serializers.StringRelatedField()

    class Meta:
        model = PaymentStatusLog
        fields = '__all__'
