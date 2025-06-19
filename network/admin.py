from django.contrib import admin
from analytics.admin_dashboard import custom_admin_site
from .models import Network

class NetworkAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']  # ✅ কেবল বিদ্যমান ফিল্ড ব্যবহার করা হয়েছে

custom_admin_site.register(Network, NetworkAdmin)
