from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ManagerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    telegram_handle = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='managers/', blank=True)

    def __str__(self):
        return self.full_name


class AffiliateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='affiliate_profile')
    manager = models.ForeignKey(ManagerProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name='affiliates')

    def __str__(self):
        return self.user.email
