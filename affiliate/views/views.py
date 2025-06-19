#affiliate\views\views.py

import os
import requests
from django.shortcuts import render
from affiliate.serializers import RegisterAffiliateSerializer
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

load_dotenv()  # Load all keys from .env

# ✅ Send Telegram message
def send_telegram_notification(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        return  # Config missing

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except requests.RequestException:
        pass

# ✅ Register view
def register_page(request):
    site_key = os.getenv("RECAPTCHA_SITE_KEY", "")
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY", "")
    message = None
    message_type = "error"

    if request.method == "POST":
        data = request.POST.dict()

        # Rename fields to match serializer
        data["confirm_password"] = data.pop("repeat_password", "")
        data["telegram"] = data.pop("messenger", "")
        data["main_verticals"] = data.pop("vertical", "")
        data["address"] = data.pop("address_zipcode", "")
        recaptcha_token = data.pop("g-recaptcha-response", "")

        # ✅ reCAPTCHA verification
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {
            'secret': secret_key,
            'response': recaptcha_token
        }
        recaptcha_result = requests.post(verify_url, data=payload).json()

        if not recaptcha_result.get("success"):
            message = "❌ reCAPTCHA failed. Please try again."
        else:
            serializer = RegisterAffiliateSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                message = "✅ Registration successful! Please check your email."
                message_type = "success"

                # ✅ Send Telegram notification
                telegram_msg = (
                    f"📥 <b>New Affiliate Registered</b>\n\n"
                    f"👤 {user.first_name} {user.last_name}\n"
                    f"📧 {user.email}\n"
                    f"🌍 {user.affiliateprofile.country}"
                )
                send_telegram_notification(telegram_msg)
            else:
                message = serializer.errors

    return render(request, "affiliate/register.html", {
        "site_key": site_key,
        "message": message,
        "message_type": message_type
    })


class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.main_profile  # কারণ related_name='main_profile'
        data = {
            "total_balance": profile.total_balance,
            "available_balance": profile.available_balance,
        }
        return Response(data)
