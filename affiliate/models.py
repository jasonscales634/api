#affiliate\models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class AffiliateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='affiliate_profile')
    company_name = models.CharField(max_length=255, blank=True)
    website = models.URLField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    telegram = models.CharField(max_length=100)
    main_verticals = models.CharField(max_length=255)
    monthly_revenue = models.CharField(max_length=100)
    traffic_sources = models.TextField()

    def __str__(self):
        return f"{self.user.email}'s Affiliate Profile"


class AffiliateDailyStat(models.Model):
    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE, related_name='daily_stats')
    date = models.DateField()
    clicks = models.IntegerField(default=0)
    conversions = models.IntegerField(default=0)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('affiliate', 'date')

    def __str__(self):
        return f"{self.affiliate.user.email} - {self.date}"
