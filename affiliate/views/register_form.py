#affiliate\views\register_form.py
import os
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from dotenv import load_dotenv

load_dotenv()

@csrf_exempt
def register_page(request):
    if request.method == "GET":
        site_key = os.getenv("RECAPTCHA_SITE_KEY", "dummy_fallback")
        return render(request, 'affiliate/register.html', {"site_key": site_key})

    elif request.method == "POST":
        data = request.POST

        # ✅ reCAPTCHA validation
        recaptcha_response = data.get("g-recaptcha-response")
        if not recaptcha_response:
            return JsonResponse({"error": "reCAPTCHA is required"}, status=400)

        recaptcha_secret = os.getenv("RECAPTCHA_SECRET_KEY")
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {
            'secret': recaptcha_secret,
            'response': recaptcha_response
        }

        try:
            recaptcha_result = requests.post(verify_url, data=payload, timeout=5).json()
        except requests.RequestException:
            return JsonResponse({"error": "Could not verify reCAPTCHA. Please try again."}, status=502)

        if not recaptcha_result.get("success"):
            return JsonResponse({"error": "reCAPTCHA verification failed"}, status=400)

        # ✅ Password match check
        if data.get("password") != data.get("confirm_password"):
            return JsonResponse({"error": "Passwords do not match"}, status=400)

        # ✅ Build JSON payload for internal API
        json_payload = {
            "email": data.get("email"),
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "password": data.get("password"),
            "confirm_password": data.get("confirm_password"),
            "company_name": data.get("company_name", ""),
            "website": data.get("website"),
            "address": data.get("address_zipcode"),  # make sure this field name matches HTML
            "city": data.get("city"),
            "country": data.get("country"),
            "telegram": data.get("messenger"),
            "main_verticals": data.get("vertical"),
            "monthly_revenue": data.get("monthly_revenue"),
            "traffic_sources": data.get("traffic_sources"),
        }

        # ✅ Send to backend API
        try:
            api_url = os.getenv("AFFILIATE_REGISTER_API_URL", "http://127.0.0.1:8000/api/affiliate/register/")
            response = requests.post(api_url, json=json_payload, timeout=10)
            result = response.json()

            if response.status_code == 201:
                return JsonResponse({
                    "message": "✅ Registration successful. Please verify your email. Once verified, admin will review your account."
                }, status=201)

            return JsonResponse(result, status=response.status_code)

        except requests.RequestException as e:
            return JsonResponse({"error": "Internal API connection failed. Try again later."}, status=500)

        except Exception as e:
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
