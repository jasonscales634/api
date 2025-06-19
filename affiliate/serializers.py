#affiliate\serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from affiliate.models import AffiliateProfile
from rest_framework.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import uuid

User = get_user_model()


class RegisterAffiliateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    company_name = serializers.CharField(required=False, allow_blank=True)
    website = serializers.URLField(required=True)
    address = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    telegram = serializers.CharField(required=True)
    main_verticals = serializers.CharField(required=True)
    monthly_revenue = serializers.CharField(required=True)
    traffic_sources = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name',
            'password', 'confirm_password',
            'company_name', 'website', 'address', 'city', 'country',
            'telegram', 'main_verticals', 'monthly_revenue', 'traffic_sources'
        )
        read_only_fields = ('id',)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("This email is already registered.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')

        # Separate AffiliateProfile fields
        profile_fields = {
            field: validated_data.pop(field)
            for field in [
                'company_name', 'website', 'address', 'city', 'country',
                'telegram', 'main_verticals', 'monthly_revenue', 'traffic_sources'
            ]
        }

        # Generate email verification token
        verification_token = uuid.uuid4()
        token_expiry = timezone.now() + timedelta(days=1)

        # Create user
        user = User.objects.create(
            **validated_data,
            is_active=True,
            is_verified=False,
            approval_status='pending',
            verification_token=verification_token,
            token_expiry=token_expiry
        )
        user.set_password(password)
        user.save()

        # Create affiliate profile
        AffiliateProfile.objects.create(user=user, **profile_fields)

        # Prepare and send verification email
        subject = "Verify your email - ADCPA"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [user.email]

        verification_link = f"{settings.SITE_URL}/verify-email/?token={verification_token}"

        html_content = render_to_string("affiliate/email_verification.html", {
            "user": user,
            "verification_link": verification_link
        })

        msg = EmailMultiAlternatives(subject, "", from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return user


class AffiliateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateProfile
        exclude = ['user']
