from django.core.management.base import BaseCommand
from affiliate.models import AffiliateDailyStat, AffiliateProfile
from django.contrib.auth import get_user_model
from datetime import date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Insert test data for Affiliate chart'

    def handle(self, *args, **kwargs):
        username = input("Enter username for affiliate: ")
        try:
            user = User.objects.get(email=username)  # তুমি যদি email দিয়ে ইউজার ধরো
            affiliate = AffiliateProfile.objects.get(user=user)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {e}'))
            return

        for i in range(10):
            AffiliateDailyStat.objects.create(
                affiliate=affiliate,
                date=date.today() - timedelta(days=i),
                clicks=10 + i,
                conversions=2 + i,
                earnings=5.5 + i
            )

        self.stdout.write(self.style.SUCCESS('✅ Test data inserted successfully!'))
