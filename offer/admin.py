from django.urls import reverse, path
from django.utils.html import format_html
from django.shortcuts import redirect
from django.contrib import messages, admin

from analytics.admin_dashboard import custom_admin_site  # ✅ Custom admin

from .models import (
    Category, TrafficSource, Currency, Advertiser,
    Offer, Goal, Landing, OfferTrafficSource, Payout
)

# -----------------------------
# 🔹 Inline Models
# -----------------------------
class GoalInline(admin.StackedInline):
    model = Goal
    extra = 1
    show_change_link = True


class LandingInline(admin.StackedInline):
    model = Landing
    extra = 1
    show_change_link = True


class OfferTrafficSourceInline(admin.TabularInline):
    model = OfferTrafficSource
    extra = 1


class PayoutInline(admin.StackedInline):
    model = Payout
    extra = 1
    show_change_link = True


# -----------------------------
# 🔹 Offer Admin
# -----------------------------
class OfferAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'advertiser', 'status', 'revenue', 'payout',
        'start_date', 'end_date', 'visible_to_affiliates', 'is_capped_status', 'clone_offer_link'
    )
    list_filter = ('status', 'categories', 'advertiser', 'visible_to_affiliates', 'start_date')
    search_fields = ('title', 'advertiser__company', 'default_goal')
    inlines = [GoalInline, LandingInline, OfferTrafficSourceInline, PayoutInline]
    filter_horizontal = ('affiliates', 'countries', 'categories')
    readonly_fields = ('created_at', 'is_capped_status')

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'description', 'description_html', 'advertiser', 'status', 'visible_to_affiliates'),
        }),
        ('Tracking & Financial', {
            'fields': ('url', 'preview_link', 'icon', 'tracking_template', 'revenue', 'payout', 'default_goal'),
        }),
        ('Cap & Scheduling', {
            'fields': ('daily_cap', 'monthly_cap', 'total_cap', 'start_date', 'end_date', 'is_capped_status'),
        }),
        ('Meta Info', {
            'fields': ('countries', 'categories', 'affiliates', 'device', 'os', 'created_at'),
        }),
    )

    # ✅ Clone Button URL (fixed)
    def clone_offer_link(self, obj):
        url = reverse('clone_offer', args=[obj.id])  # Fixed: removed 'admin:'
        return format_html('<a class="button" href="{}">🌀 Clone</a>', url)
    clone_offer_link.short_description = 'Clone Offer'

    # ✅ Clone View Register
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('clone/<int:offer_id>/', self.admin_site.admin_view(self.clone_offer), name='clone_offer'),
        ]
        return custom_urls + urls

    # ✅ Clone Logic
    def clone_offer(self, request, offer_id):
        try:
            original = Offer.objects.get(pk=offer_id)
            cloned = Offer.objects.get(pk=offer_id)
            cloned.pk = None
            cloned.title = f"{original.title} (Clone)"
            cloned.save()

            # Clone related data
            for related_set in [original.goals.all(), original.landings.all(), original.payouts.all()]:
                for item in related_set:
                    item.pk = None
                    item.offer = cloned
                    item.save()

            for ots in OfferTrafficSource.objects.filter(offer=original):
                ots.pk = None
                ots.offer = cloned
                ots.save()

            messages.success(request, f"✅ Offer '{original.title}' cloned successfully!")
            return redirect(f"/admin/offer/offer/{cloned.id}/change/")
        except Offer.DoesNotExist:
            messages.error(request, "❌ Offer not found.")
            return redirect("/admin/offer/offer/")

    # Cap Status
    def is_capped_status(self, obj):
        status = obj.is_capped()
        color = 'red' if status else 'green'
        label = 'CAPPED' if status else 'OK'
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, label)
    is_capped_status.short_description = 'Cap Status'


# -----------------------------
# 🔹 Register Models to Custom Admin Site
# -----------------------------
custom_admin_site.register(Offer, OfferAdmin)
custom_admin_site.register(Category)
custom_admin_site.register(TrafficSource)
custom_admin_site.register(Currency)
custom_admin_site.register(Advertiser)
