# ✅ admin.py
from django.contrib import admin
from .models import UserBillingInfo

@admin.register(UserBillingInfo)
class BillingInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'currency', 'verified')
    list_filter = ('verified', 'currency')
    search_fields = ('user__email', 'account_number', 'payment_email')
