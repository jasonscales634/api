#model.py

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from countries_plus.models import Country
import json

# ---------------------
# ✅ Category Model
# ---------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def _str_(self):
        return self.name


# ---------------------
# ✅ TrafficSource Model
# ---------------------
class TrafficSource(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def _str_(self):
        return self.name


# ---------------------
# ✅ Currency Model
# ---------------------
class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)

    def _str_(self):
        return self.code


# ---------------------
# ✅ Advertiser Model
# ---------------------
class Advertiser(models.Model):
    company = models.CharField(max_length=255)
    email = models.EmailField()
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    messenger = models.CharField(max_length=255, blank=True, null=True)
    site = models.URLField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def _str_(self):
        return self.company


# ---------------------
# ✅ Offer Model
# ---------------------
class Offer(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('deleted', 'Deleted'),
    ]

    title = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(blank=True)
    description_html = models.TextField(blank=True, default='')
    preview_link = models.URLField(blank=True, null=True)

    icon = models.ImageField(upload_to='offer_icons/', blank=True, null=True)

    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    payout = models.DecimalField(max_digits=10, decimal_places=2)
    default_goal = models.CharField(max_length=100, default="Default Goal")

    os = models.CharField(max_length=100)
    device = models.CharField(max_length=100, default="All")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_deleted = models.BooleanField(default=False)

    daily_cap = models.PositiveIntegerField(null=True, blank=True)
    monthly_cap = models.PositiveIntegerField(null=True, blank=True)
    total_cap = models.PositiveIntegerField(null=True, blank=True)
    cap_tracking = models.JSONField(default=dict, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    affiliates = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='affiliate_offers'
    )
    visible_to_affiliates = models.BooleanField(default=True)

    countries = models.ManyToManyField('countries_plus.Country', blank=True)
    categories = models.ManyToManyField('Category', blank=True)

    tracking_template = models.TextField(null=True, blank=True)
    advertiser = models.ForeignKey('Advertiser', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def clean(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError("End date must be after start date.")
        if isinstance(self.cap_tracking, str):
            raise ValidationError({"cap_tracking": "Must be a valid JSON object, not a string."})

    def is_capped(self):
        today_str = timezone.now().date().isoformat()
        tracking = self.cap_tracking.get(today_str, {"daily": 0, "monthly": 0, "total": 0})
        return (
            (self.daily_cap and tracking["daily"] >= self.daily_cap) or
            (self.monthly_cap and tracking["monthly"] >= self.monthly_cap) or
            (self.total_cap and tracking["total"] >= self.total_cap)
        )

    def increase_cap_count(self):
        today_str = timezone.now().date().isoformat()
        tracking = self.cap_tracking.get(today_str, {"daily": 0, "monthly": 0, "total": 0})
        tracking["daily"] += 1
        tracking["monthly"] += 1
        tracking["total"] += 1
        self.cap_tracking[today_str] = tracking
        self.save(update_fields=["cap_tracking"])

    def get_tracking_url(self, **kwargs):
        """
        Replace macros like {click_id}, {pid}, {sub1}, etc.
        Priority: tracking_template > DEFAULT_TRACKING_TEMPLATE
        """
        from django.conf import settings
        url = self.tracking_template or getattr(settings, 'DEFAULT_TRACKING_TEMPLATE', '')
        for key, value in kwargs.items():
            url = url.replace(f'{{{key}}}', str(value))
        return url

    def save(self, *args, **kwargs):
        if not self.tracking_template:
            self.tracking_template = (
                "http://127.0.0.1:8000/redirect/?click_id={click_id}&pid={pid}"
                "&sub1={sub1}&sub2={sub2}&sub3={sub3}&sub4={sub4}&sub5={sub5}"
            )
        super().save(*args, **kwargs)


# ---------------------
# ✅ Goal Model
# ---------------------
class Goal(models.Model):
    offer = models.ForeignKey(Offer, related_name="goals", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    payout = models.DecimalField(max_digits=10, decimal_places=2)
    revenue = models.DecimalField(max_digits=10, decimal_places=2)

    def _str_(self):
        return f"{self.offer.title} - {self.name}"

    class Meta:
        unique_together = ('offer', 'name')


# ---------------------
# ✅ Landing Model
# ---------------------
class Landing(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='landings')
    name = models.CharField(max_length=255)
    url = models.URLField()
    is_active = models.BooleanField(default=True)

    def _str_(self):
        return f"{self.offer.title} - {self.name}"

    class Meta:
        unique_together = ('offer', 'name')


# ---------------------
# ✅ OfferTrafficSource Model
# ---------------------
class OfferTrafficSource(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    traffic_source = models.ForeignKey(TrafficSource, on_delete=models.CASCADE)
    allowed = models.BooleanField(default=True)

    def _str_(self):
        return f"{self.offer.title} - {self.traffic_source.name}"

    class Meta:
        unique_together = ('offer', 'traffic_source')


# ---------------------
# ✅ Payout Model
# ---------------------
class Payout(models.Model):
    TYPE_CHOICES = (
        ('fixed', 'Fixed'),
        ('percent', 'Percent'),
    )

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='payouts')
    goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, blank=True, related_name="payouts")
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    countries = models.ManyToManyField(Country, blank=True)
    payout = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='fixed')

    def _str_(self):
        return f"{self.offer.title} - {self.payout} {self.currency.code if self.currency else ''}"

    class Meta:
        verbose_name = "Payout"
        verbose_name_plural = "Payouts"