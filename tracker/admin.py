from django.contrib import admin
from analytics.admin_dashboard import custom_admin_site
from .models import Click, Conversion


@admin.register(Click, site=custom_admin_site)
class ClickAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'affiliate',
        'offer',
        'ip',
        'country',
        'device',
        'os',
        'revenue',
        'payout',
        'sub1',
        'sub2',
        'sub3',
        'sub4',
        'sub5',
        'host',
    )
    search_fields = (
        'ip',
        'country',
        'offer__title',
        'affiliate__username',
        'device',
        'os',
        'sub1',
        'sub2',
        'sub3',
        'sub4',
        'sub5',
    )
    list_filter = (
        'country',
        'affiliate',
        'offer',
        'device',
        'os',
        'created_at',
    )
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')


@admin.register(Conversion, site=custom_admin_site)
class ConversionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'created_at',
        'affiliate',
        'offer',
        'goal',
        'status',
        'payout',
        'revenue',
        'country',
        'city',
        'device',
        'os',
        'sub1',
        'sub2',
        'sub3',
        'sub4',
        'sub5',
        'ip',
    )
    search_fields = (
        'ip',
        'country',
        'city',
        'offer__title',
        'affiliate__username',
        'goal_value',
        'status',
        'device',
        'os',
        'sub1',
        'sub2',
        'sub3',
        'sub4',
        'sub5',
    )
    list_filter = (
        'status',
        'country',
        'city',
        'affiliate',
        'offer',
        'device',
        'os',
        'created_at',
    )
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
