# affiliate/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import AffiliateProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_affiliate_profile(sender, instance, created, **kwargs):
    if created:
        AffiliateProfile.objects.create(user=instance)
