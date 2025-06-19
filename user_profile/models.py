#user_profile\models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid


# ------------------------
# Helper function
# ------------------------
def one_day_later():
    return timezone.now() + timedelta(days=1)


# ------------------------
# Custom User Manager
# ------------------------
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# ------------------------
# Custom User Model
# ------------------------
class User(AbstractUser):
    username = None  # disable username
    email = models.EmailField(_('email address'), unique=True)

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('affiliate', 'Affiliate'),
        ('advertiser', 'Advertiser'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='affiliate')

    # Email verification
    is_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, null=True, blank=True)
    token_expiry = models.DateTimeField(default=one_day_later)

    # Manual approval
    is_active = models.BooleanField(default=False)

    # Password reset
    reset_token = models.UUIDField(null=True, blank=True, unique=True)
    reset_token_expiry = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# ------------------------
# User Profile Model
# ------------------------
from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='main_profile'
    )

    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)

    company = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    telegram = models.CharField(max_length=100, blank=True, null=True)
    main_verticals = models.TextField(blank=True, null=True)
    monthly_revenue = models.CharField(max_length=100, blank=True, null=True)
    traffic_sources = models.TextField(blank=True, null=True)

    total_balance = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    available_balance = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)  # ✅ Newly added

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_affiliates'
    )

    def __str__(self):
        return f"Profile of {self.user.email}"
