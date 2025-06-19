# analytics/statistics/views/export_csv.py

import csv
from django.http import HttpResponse
from analytics.statistics.models.statistics import DailyStat

def export_combined_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="combined_stats.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Country', 'Device', 'OS', 'Raw Clicks', 'Unique Clicks', 'Conversions', 'Revenue', 'Earning'])

    stats = DailyStat.objects.all().order_by('-date')

    # Optional filter by affiliate (coming in step 2)
    affiliate_id = request.GET.get('affiliate')
    if affiliate_id:
        stats = stats.filter(affiliate_id=affiliate_id)

    for stat in stats:
        writer.writerow([
            stat.date, stat.country, stat.device, stat.os,
            stat.raw_clicks, stat.unique_clicks,
            stat.conversions, stat.revenue, stat.earning
        ])

    return response
