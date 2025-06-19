from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from django.db import DatabaseError

from analytics.statistics.models.statistics import DailyStat
from tracker.models import Click, Conversion


class Command(BaseCommand):
    help = 'Generate daily stats grouped by affiliate, country, device, OS'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write("📊 Starting DailyStat generation...")
            yesterday = timezone.now().date() - timedelta(days=1)

            # Fetch click data
            click_data = Click.objects.filter(created_at__date=yesterday).values(
                'affiliate_id', 'country', 'device', 'os'
            ).annotate(
                raw_clicks=Count('id'),
                unique_clicks=Count('sub1', distinct=True)
            )

            # Fetch conversion data
            conv_data = Conversion.objects.filter(created_at__date=yesterday).values(
                'affiliate_id', 'country', 'device', 'os'
            ).annotate(
                conversions=Count('id'),
                revenue=Sum('revenue'),
                charge=Sum('payout'),
            )

            conv_index = {
                (item['affiliate_id'], item['country'], item['device'], item['os']): item
                for item in conv_data
            }

            total_updated = 0

            for row in click_data:
                key = (row['affiliate_id'], row['country'], row['device'], row['os'])
                conv = conv_index.get(key, {})

                revenue = conv.get('revenue') or 0
                charge = conv.get('charge') or 0
                earning = revenue - charge

                DailyStat.objects.update_or_create(
                    date=yesterday,
                    affiliate_id=row['affiliate_id'],
                    country=row['country'],
                    device=row['device'],
                    os=row['os'],
                    defaults={
                        'raw_clicks': row['raw_clicks'],
                        'unique_clicks': row['unique_clicks'],
                        'conversions': conv.get('conversions', 0),
                        'revenue': revenue,
                        'charge': charge,
                        'earning': earning,
                    }
                )
                total_updated += 1

            self.stdout.write(self.style.SUCCESS(
                f"✅ {total_updated} stats generated for {yesterday}"
            ))

        except DatabaseError as e:
            self.stderr.write(self.style.ERROR(f"❌ Database error: {e}"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Unexpected error: {e}"))
