from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    METHOD_CHOICES = [
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
        ('crypto', 'Crypto (USDT/BTC)'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=METHOD_CHOICES)
    currency = models.CharField(max_length=10, default='USD')

    # Method-specific fields
    account_number = models.CharField(max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    payment_email = models.EmailField(blank=True, null=True)
    wallet_address = models.CharField(max_length=150, blank=True, null=True)
    crypto_network = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} - {self.method} - {self.status}"


class StatusLog(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="logs")
    previous_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Payment {self.payment.id} changed from {self.previous_status} to {self.new_status}"


class PaymentStatusLog(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"Payment {self.payment.id}: {self.old_status} → {self.new_status}"
