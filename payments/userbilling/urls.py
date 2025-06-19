# userbilling/urls.py
from django.urls import path
from .views import(
    create_billing_info,
    get_billing_info,
    verify_billing_code,
    resend_verification_code,
)

urlpatterns = [
    path('create/', create_billing_info),
    path('get/', get_billing_info),
    path('verify/', verify_billing_code),
    path('resend-code/', resend_verification_code),
]