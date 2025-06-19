from django.db import models
from django.contrib.auth import get_user_model
from offer.models import Offer
from tracker.models import conversion_statuses

User = get_user_model()

CREATED_STATUS = 'created'

POSTBACK_STATUSES = (
    ('created', 'Created'),
    ('not_found', 'Not Found'),
) + conversion_statuses


class Postback(models.Model):
    url = models.CharField(max_length=500)
    status = models.CharField(
        max_length=20,
        choices=POSTBACK_STATUSES,
        default=CREATED_STATUS
    )
    goal = models.CharField(max_length=20, blank=True, default="")

    offer = models.ForeignKey(
        Offer,
        related_name='postbacks',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    affiliate = models.ForeignKey(
        User,
        related_name='postbacks',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Postback ({self.affiliate_id}) -> {self.url}"


class Log(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=500)
    response_status = models.CharField(max_length=10, default='')
    response_text = models.TextField()

    affiliate = models.ForeignKey(
        User,
        related_name='postback_logs',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Log ({self.affiliate_id}) [{self.response_status}]"
