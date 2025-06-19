#C:\Users\MD BASARULL ISLAM\Downloads\adcpaapi1-main (1)\adcpaapi1-main\affiliate\views\register.py

import os
import requests
from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from affiliate.serializers import RegisterAffiliateSerializer
from dotenv import load_dotenv

load_dotenv()  # .env ফাইল থেকে RECAPTCHA key ইত্যাদি লোড করবে

def register_page(request):
    site_key = os.getenv("RECAPTCHA_SITE_KEY", "")
    secret_key = os.getenv("RECAPTCHA_SECRET_KEY", "")
    message = None
    message_type = "error"

    if request.method == "POST":
        # Step 1: Form Data Prepare
        data = request.POST.dict()
        data["confirm_password"] = data.pop("repeat_password", "")
        data["telegram"] = data.pop("messenger", "")
        data["main_verticals"] = data.pop("vertical", "")
        data["address"] = data.pop("address_zipcode", "")
        recaptcha_token = data.pop("g-recaptcha-response", "")

        # Step 2: Verify reCAPTCHA
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {
            'secret': secret_key,
            'response': recaptcha_token
        }
        recaptcha_result = requests.post(verify_url, data=payload).json()

        if not recaptcha_result.get("success"):
            message = "❌ reCAPTCHA failed. Please try again."
        else:
            # Step 3: Validate and Save using DRF serializer
            serializer = RegisterAffiliateSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                message = "✅ Registration successful! Please check your email."
                message_type = "success"
            else:
                message = serializer.errors

    return render(request, "affiliate/register.html", {
        "site_key": site_key,
        "message": message,
        "message_type": message_type
    })




