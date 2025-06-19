from rest_framework import serializers
from .models import ManagerProfile, AffiliateProfile

class ManagerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManagerProfile
        fields = ['full_name', 'email', 'telegram_handle', 'photo']


class AffiliateDashboardSerializer(serializers.ModelSerializer):
    manager = ManagerProfileSerializer()

    class Meta:
        model = AffiliateProfile
        fields = ['manager']
