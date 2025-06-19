# affiliate/admin.py
from django.contrib import admin
from analytics.admin_dashboard import custom_admin_site
from .models import AffiliateProfile

@admin.register(AffiliateProfile, site=custom_admin_site)
class AffiliateProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'company_name', 'website', 'city', 'country')
    search_fields = ('user__username', 'user__email', 'company_name')
    list_filter = ('country',)
    ordering = ('-id',)