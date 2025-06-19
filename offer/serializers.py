import json
from rest_framework import serializers
from .models import Offer, Goal, Landing
from countries_plus.models import Country


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ["id", "name", "payout", "revenue"]


class LandingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landing
        fields = ["id", "offer", "name", "url", "is_active"]
        read_only_fields = ["offer"]


class OfferSerializer(serializers.ModelSerializer):
    goals = GoalSerializer(many=True, required=False)
    landings = LandingSerializer(many=True, read_only=True)
    goal_count = serializers.SerializerMethodField()
    cap_tracking = serializers.SerializerMethodField()
    is_capped = serializers.SerializerMethodField()  # ✅ New field
    icon = serializers.ImageField(required=False, allow_null=True)

    countries = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)
    devices = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Offer
        fields = [
            "id", "title", "url", "description", "description_html",
            "preview_link", "icon", "revenue", "payout", "default_goal",
            "os", "device", "devices", "status", "daily_cap", "monthly_cap", "total_cap",
            "cap_tracking", "is_capped", "start_date", "end_date", "goal_count",
            "affiliates", "visible_to_affiliates", "countries", "categories",
            "tracking_template", "advertiser", "created_at",
            "goals", "landings",
        ]
        read_only_fields = ("id", "created_at", "goal_count", "cap_tracking", "is_capped")

    def get_goal_count(self, obj):
        return obj.goals.count()

    def get_cap_tracking(self, obj):
        return getattr(obj, "cap_tracking", {})

    def get_is_capped(self, obj):
        return obj.is_capped() if hasattr(obj, 'is_capped') else False

    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("End date must be after start date.")
        return data

    def to_internal_value(self, data):
        if isinstance(data.get("goals"), str):
            try:
                data["goals"] = json.loads(data["goals"])
            except Exception:
                raise serializers.ValidationError({"goals": "Invalid JSON format"})
        return super().to_internal_value(data)

    def create(self, validated_data):
        goals_data = validated_data.pop("goals", [])
        affiliates = validated_data.pop("affiliates", [])
        categories = validated_data.pop("categories", [])
        countries_codes = validated_data.pop("countries", [])
        devices = validated_data.pop("devices", [])

        offer = Offer.objects.create(**validated_data)

        if devices:
            offer.device = ",".join(devices)
            offer.save()

        if countries_codes:
            country_objs = Country.objects.filter(iso__in=countries_codes)
            offer.countries.set(country_objs)

        offer.affiliates.set(affiliates)
        offer.categories.set(categories)

        for goal in goals_data:
            Goal.objects.create(offer=offer, **goal)

        return offer

    def update(self, instance, validated_data):
        goals_data = validated_data.pop("goals", None)
        affiliates = validated_data.pop("affiliates", None)
        categories = validated_data.pop("categories", None)
        countries_codes = validated_data.pop("countries", None)
        devices = validated_data.pop("devices", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if devices is not None:
            instance.device = ",".join(devices)
            instance.save()

        if affiliates is not None:
            instance.affiliates.set(affiliates)
        if categories is not None:
            instance.categories.set(categories)
        if countries_codes is not None:
            instance.countries.set(Country.objects.filter(iso__in=countries_codes))

        if goals_data is not None:
            instance.goals.all().delete()
            for goal in goals_data:
                Goal.objects.create(offer=instance, **goal)

        return instance
