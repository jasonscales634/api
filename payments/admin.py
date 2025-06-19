from django.contrib import admin
from analytics.admin_dashboard import custom_admin_site  # ✅ Custom admin site import
from .models import Payment, StatusLog, PaymentStatusLog


@admin.register(Payment, site=custom_admin_site)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'amount', 'method', 'currency',
        'account_number', 'bank_name', 'wallet_address',
        'crypto_network', 'payment_email',
        'status', 'is_deleted', 'created_at'
    )
    search_fields = (
        'user__email', 'account_number', 'bank_name',
        'wallet_address', 'crypto_network', 'payment_email'
    )
    list_filter = ('status', 'method', 'is_deleted', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(StatusLog, site=custom_admin_site)
class StatusLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'payment', 'previous_status', 'new_status',
        'updated_by', 'updated_at'
    )
    list_filter = ('new_status', 'updated_by')
    search_fields = ('payment__id', 'updated_by__email')
    readonly_fields = ('updated_at',)


@admin.register(PaymentStatusLog, site=custom_admin_site)
class PaymentStatusLogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'payment', 'old_status', 'new_status',
        'changed_by', 'changed_at'
    )
    list_filter = ('new_status', 'changed_by')
    search_fields = ('payment__id', 'changed_by__email')
    readonly_fields = ('changed_at',)
