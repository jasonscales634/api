from django.db import models
from affiliate.models import AffiliateProfile
from offer.models import Offer
from tracker.models import Conversion  # ✅ এটি যোগ করো

class Click(models.Model):
    ip = models.GenericIPAddressField()
    user_agent = models.TextField()

    country = models.CharField(max_length=5, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    device = models.CharField(max_length=50, blank=True, null=True)
    os = models.CharField(max_length=50, blank=True, null=True)
    browser = models.CharField(max_length=50, blank=True, null=True)

    referrer = models.URLField(blank=True, null=True)
    sub1 = models.CharField(max_length=100, blank=True, null=True)
    sub2 = models.CharField(max_length=100, blank=True, null=True)
    sub3 = models.CharField(max_length=100, blank=True, null=True)
    sub4 = models.CharField(max_length=100, blank=True, null=True)
    sub5 = models.CharField(max_length=100, blank=True, null=True)

    ios_idfa = models.CharField(max_length=100, blank=True, null=True)
    android_id = models.CharField(max_length=100, blank=True, null=True)

    cbid = models.CharField(max_length=100, blank=True, null=True)
    uniq = models.BooleanField(default=False)

    affiliate = models.ForeignKey(AffiliateProfile, on_delete=models.SET_NULL, null=True, blank=True)
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)

    # ✅ এখানে স্ট্রিং 'analytics.Conversion' বাদ দিয়ে সরাসরি model class ব্যবহার করো
    conversion = models.OneToOneField(
        Conversion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='click_record'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Click from {self.ip} at {self.created_at}"
