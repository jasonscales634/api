
#C:\Users\MD BASARULL ISLAM\Downloads\adcpaapi1-main (1)\adcpaapi1-main\analytics\statistics\serializers\conversions.py

from rest_framework import serializers

from tracker.models import Conversion

class ConversionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversion
        fields = [
            'click', 'goal', 'revenue', 'payout',
            'status', 'transaction_id', 'created_at'
        ]
