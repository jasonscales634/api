from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import Profile

User = get_user_model()


# ------------------------------
# 👤 User Info Serializer
# ------------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active']


# ------------------------------
# 🔐 JWT Login via Email
# ------------------------------
class EmailLoginSerializer(TokenObtainPairSerializer):
    # ⚠️ If EMAIL_FIELD not defined in your custom user model, use hardcoded field:
    # username_field = 'email'
    username_field = getattr(User, 'EMAIL_FIELD', 'email')

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        user = authenticate(request=self.context.get("request"), email=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        # ⚠️ Ensure your user model has 'is_verified'
        if not getattr(user, 'is_verified', False):
            raise serializers.ValidationError("Please verify your email address first.")

        if not user.is_active:
            raise serializers.ValidationError("Your account is pending approval.")

        data = super().validate(attrs)
        data["user"] = UserSerializer(user).data
        return data


# ------------------------------
# ✉️ Password Reset Email Sender
# ------------------------------
def send_password_reset_email(user):
    user.reset_token = uuid.uuid4()
    user.reset_token_expiry = timezone.now() + timedelta(hours=24)
    user.save()

    reset_url = f"{settings.FRONTEND_URL}/reset-password/?token={user.reset_token}"

    subject = "🔒 Reset Your ADCpa Password"
    message = f"""
Hi {user.email},

You requested a password reset. Click the link below to set a new password:

{reset_url}

This link is valid for 24 hours.

If you did not request a reset, ignore this email.

— ADCpa Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


# ------------------------------
# ✅ Email Verification Sender
# ------------------------------
def send_verification_email(user):
    user.verification_token = uuid.uuid4()
    user.token_expiry = timezone.now() + timedelta(days=1)
    user.save()

    verify_url = f"{settings.FRONTEND_URL}/verify-email/?token={user.verification_token}"

    subject = "✅ Verify Your Email - ADCpa"
    message = f"""
Hi {user.email},

Please verify your email within 24 hours by clicking the link below:

{verify_url}

Thanks,
ADCpa Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )


# ------------------------------
# 📝 Profile Serializer
# ------------------------------
class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    login = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = [
            'email',
            'login',
            'first_name',
            'last_name',
            'company',
            'website',
            'phone',  # ✅ Make sure your Profile model includes this field
            'address',
            'city',
            'country',
            'telegram',
            'main_verticals',
            'monthly_revenue',
            'traffic_sources',
        ]
