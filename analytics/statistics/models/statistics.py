from django.db import models
from affiliate.models import AffiliateProfile
from offer.models import Offer  # ✅ Offer import করো

class DailyStat(models.Model):
    date = models.DateField()
    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.CASCADE)

    # ✅ updated: allow null and blank to avoid migration errors
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, null=True, blank=True)

    country = models.CharField(max_length=5)
    device = models.CharField(max_length=50)
    os = models.CharField(max_length=50)

    raw_clicks = models.IntegerField()
    unique_clicks = models.IntegerField()
    conversions = models.IntegerField()
    revenue = models.FloatField()
    charge = models.FloatField()
    earning = models.FloatField()

    class Meta:
        verbose_name = "Daily Stat"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date} - {self.affiliate} - {self.offer}"