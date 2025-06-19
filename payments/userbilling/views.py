import random
from datetime import timedelta

from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UserBillingInfo, BillingVerificationCode
from .serializers import UserBillingInfoSerializer


# ✅ Create Billing Info and Send Verification Email
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_billing_info(request):
    user = request.user

    if hasattr(user, 'billing_info'):
        return Response({"error": "Billing info already exists."}, status=400)

    serializer = UserBillingInfoSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        billing_info = serializer.save(user=user)
        code = billing_info.generate_verification_code()

        # ✅ Send HTML email
        subject = "Billing Info Verification Code"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

        text_content = f"Your verification code is {code}"
        html_content = render_to_string("emails/verification_code.html", {"code": code, "user": user})

        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        return Response({"message": "Billing info created. Verification code sent."})

    return Response(serializer.errors, status=400)


# ✅ Verify Code & Activate Billing Info
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_billing_code(request):
    user = request.user
    code = request.data.get("code")

    if not code:
        return Response({"error": "Code is required."}, status=400)

    try:
        verification = BillingVerificationCode.objects.filter(
            user=user, code=code, is_used=False
        ).latest('created_at')
    except BillingVerificationCode.DoesNotExist:
        return Response({"error": "Invalid or expired code."}, status=400)

    if not verification.is_valid():
        return Response({"error": "Code has expired."}, status=400)

    # ✅ Mark code used and verify billing
    verification.is_used = True
    verification.save()

    try:
        billing = user.billing_info
        billing.verified = True
        billing.save()
    except UserBillingInfo.DoesNotExist:
        return Response({"error": "Billing info not found."}, status=404)

    return Response({"message": "Billing info verified successfully."})


# ✅ Re-send Verification Code (Optional)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_verification_code(request):
    user = request.user
    try:
        billing = user.billing_info
    except UserBillingInfo.DoesNotExist:
        return Response({"error": "No billing info found."}, status=404)

    # ❌ Mark previous codes as used
    BillingVerificationCode.objects.filter(user=user, is_used=False).update(is_used=True)

    code = str(random.randint(100000, 999999))
    expires = timezone.now() + timedelta(minutes=10)

    BillingVerificationCode.objects.create(
        user=user, code=code, expires_at=expires
    )

    html = render_to_string("emails/verification_code.html", {
        "user": user,
        "code": code,
        "expires_at": expires.strftime('%I:%M %p')
    })

    email = EmailMultiAlternatives(
        subject="Verify Your Payment Method",
        body=f"Your code is: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html, "text/html")
    email.send()

    return Response({"message": "Verification code re-sent to your email."})


# ✅ Get Current Billing Info
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_billing_info(request):
    try:
        billing = request.user.billing_info
    except UserBillingInfo.DoesNotExist:
        return Response({"error": "No billing info found."}, status=404)

    serializer = UserBillingInfoSerializer(billing)
    return Response(serializer.data)
