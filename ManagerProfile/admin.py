from django.contrib import admin
from analytics.admin_dashboard import custom_admin_site  # ✅ Custom admin site import

from .models import ManagerProfile, AffiliateProfile

class ManagerProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'telegram_handle']

class AffiliateProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'manager']

# ✅ Registering to custom admin site
custom_admin_site.register(ManagerProfile, ManagerProfileAdmin)
custom_admin_site.register(AffiliateProfile, AffiliateProfileAdmin)
