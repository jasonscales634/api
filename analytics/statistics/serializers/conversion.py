from rest_framework import serializers
from tracker.models import Conversion
from analytics.statistics.models.clicks import Click
from offer.models import Goal, Currency


class ConversionCreateSerializer(serializers.ModelSerializer):
    click = serializers.PrimaryKeyRelatedField(queryset=Click.objects.all(), required=False)
    goal = serializers.PrimaryKeyRelatedField(queryset=Goal.objects.all(), required=False)
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all(), required=False)

    class Meta:
        model = Conversion
        fields = [
            'transaction_id',
            'click',
            'goal',
            'revenue',
            'payout',
            'status',
            'currency',
            'sub1', 'sub2', 'sub3', 'sub4', 'sub5',
            'country', 'ip', 'ua', 'comment'
        ]

    def validate(self, data):
        transaction_id = data.get('transaction_id')
        if Conversion.objects.filter(transaction_id=transaction_id).exists():
            raise serializers.ValidationError({"transaction_id": "This transaction_id already exists."})

        if data.get('click') and data.get('goal'):
            if data['goal'].offer != data['click'].offer:
                raise serializers.ValidationError("Goal does not match the offer associated with the click.")

        return data

    def create(self, validated_data):
        goal = validated_data.get('goal')
        if goal:
            validated_data.setdefault('revenue', goal.revenue)
            validated_data.setdefault('payout', goal.payout)

        return Conversion.objects.create(**validated_data)
