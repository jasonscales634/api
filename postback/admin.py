from django.contrib import admin
from analytics.admin_dashboard import custom_admin_site  # ✅ Import your custom admin
from .models import Postback, Log


@admin.register(Postback, site=custom_admin_site)
class PostbackAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'affiliate',
        'offer',
        'status',
        'goal',
        'url',
    )


@admin.register(Log, site=custom_admin_site)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'affiliate',
        'url',
        'response_status',
    )
