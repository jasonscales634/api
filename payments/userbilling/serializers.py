# ✅ serializers.py
from rest_framework import serializers
from .models import UserBillingInfo

class UserBillingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBillingInfo
        exclude = ['verification_code']  # Don't expose in API
        read_only_fields = ['verified']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user != instance.user:
            raise serializers.ValidationError("Not allowed to update other users' billing info.")
        raise serializers.ValidationError("Editing billing info is not allowed. Contact admin.")