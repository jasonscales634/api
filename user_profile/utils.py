# user_profile/utils.py

import uuid
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


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

If you did not request a reset, please ignore this email.

– ADCpa Team
"""
    send_mail(
        subject=subject,
        message=message.strip(),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )


def send_verification_email(user):
    user.verification_token = uuid.uuid4()
    user.token_expiry = timezone.now() + timedelta(days=1)
    user.save()

    verify_url = f"{settings.FRONTEND_URL}/verify-email/?token={user.verification_token}"

    subject = "✅ Verify Your Email - ADCpa"
    message = f"""
Hi {user.email},

Please verify your email by clicking the link below. This link is valid for 24 hours:

{verify_url}

Thanks,
ADCpa Team
"""
    send_mail(
        subject=subject,
        message=message.strip(),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False
    )
