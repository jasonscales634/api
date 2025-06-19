# ✅ C:\...\payments\userbilling\models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import random

User = get_user_model()


class UserBillingInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='billing_info')
    account_number = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    payment_email = models.EmailField(blank=True, null=True)
    wallet_address = models.CharField(max_length=150, blank=True, null=True)
    crypto_network = models.CharField(max_length=50, blank=True, null=True)
    currency = models.CharField(max_length=10, default='USD')
    verified = models.BooleanField(default=False)

    def generate_verification_code(self):
        """
        Helper method: Creates a verification code object for this user.
        """
        code = str(random.randint(100000, 999999))
        expires = timezone.now() + timezone.timedelta(minutes=10)
        BillingVerificationCode.objects.create(user=self.user, code=code, expires_at=expires)
        return code

    def __str__(self):
        return f"Billing Info for {self.user.email}"


class BillingVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.code}"
