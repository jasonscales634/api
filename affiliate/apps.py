# ✅ affiliate/apps.py
from django.apps import AppConfig

class AffiliateConfig(AppConfig):
    name = 'affiliate'

    # Optional: Uncomment if you add signals later
    # def ready(self):
    #     import affiliate.signals
