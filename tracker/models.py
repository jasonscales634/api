#\tracker\models.py

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from offer.models import Offer, Goal, Currency

User = get_user_model()

# ------------------------------
# 🔸 Conversion Status Choices
# ------------------------------
APPROVED_STATUS = 'approved'
HOLD_STATUS = 'hold'
REJECTED_STATUS = 'rejected'
PENDING_STATUS = 'pending'

conversion_statuses = (
    (APPROVED_STATUS, 'Approved'),
    (HOLD_STATUS, 'Hold'),
    (REJECTED_STATUS, 'Rejected'),
    (PENDING_STATUS, 'Pending'),
)

# ------------------------------
# 🔸 Click Model
# ------------------------------
class Click(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    sub1 = models.CharField(max_length=500, blank=True, default="")
    sub2 = models.CharField(max_length=500, blank=True, default="")
    sub3 = models.CharField(max_length=500, blank=True, default="")
    sub4 = models.CharField(max_length=500, blank=True, default="")
    sub5 = models.CharField(max_length=500, blank=True, default="")

    ip = models.GenericIPAddressField()
    country = models.CharField(max_length=2, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, null=True)
    ua = models.CharField(max_length=200, blank=True, default="")
    os = models.CharField(max_length=100, blank=True, null=True)
    device = models.CharField(max_length=100, blank=True, null=True)

    device_time = models.DateTimeField(null=True, blank=True)
    ip_local_time = models.DateTimeField(null=True, blank=True)
    isp = models.CharField(max_length=100, blank=True, null=True)

    revenue = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    payout = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    offer = models.ForeignKey(Offer, related_name='clicks', on_delete=models.SET_NULL, null=True)
    affiliate = models.ForeignKey(User, related_name='clicks', on_delete=models.SET_NULL, null=True)
    affiliate_manager = models.ForeignKey(User, related_name='managed_clicks', on_delete=models.SET_NULL, null=True, blank=True)
    host = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)

# ------------------------------
# 🔸 Conversion Model
# ------------------------------
class Conversion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    click = models.ForeignKey(Click, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversions')
    click_date = models.DateTimeField(null=True, blank=True)

    sub1 = models.CharField(max_length=500, blank=True, default="")
    sub2 = models.CharField(max_length=500, blank=True, default="")
    sub3 = models.CharField(max_length=500, blank=True, default="")
    sub4 = models.CharField(max_length=500, blank=True, default="")
    sub5 = models.CharField(max_length=500, blank=True, default="")

    ip = models.GenericIPAddressField(null=True, blank=True)
    country = models.CharField(max_length=2, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, null=True)
    ua = models.CharField(max_length=200, blank=True, default="")
    os = models.CharField(max_length=100, blank=True, null=True)
    device = models.CharField(max_length=100, blank=True, null=True)

    device_time = models.DateTimeField(null=True, blank=True)
    ip_local_time = models.DateTimeField(null=True, blank=True)
    isp = models.CharField(max_length=100, blank=True, null=True)

    goal_value = models.CharField(max_length=20, blank=True, default="")
    sum = models.FloatField(default=0.0)
    status = models.CharField(max_length=10, choices=conversion_statuses, default=REJECTED_STATUS)
    comment = models.CharField(max_length=128, blank=True, default="")
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    revenue = models.DecimalField(max_digits=7, decimal_places=2, default=0.0)
    payout = models.DecimalField(max_digits=7, decimal_places=2, default=0.0)

    goal = models.ForeignKey(Goal, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True, blank=True)
    offer = models.ForeignKey(Offer, related_name='conversions', on_delete=models.SET_NULL, null=True)

    affiliate = models.ForeignKey(User, related_name='conversions', on_delete=models.SET_NULL, null=True)
    affiliate_manager = models.ForeignKey(User, related_name='managed_conversions', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return str(self.id)
