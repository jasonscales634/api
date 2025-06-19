# analytics/statistics/views/summary.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from analytics.statistics.models.statistics import DailyStat
from django.db.models import Sum

@api_view(['GET'])
def statistics_summary(request):
    total = DailyStat.objects.aggregate(
        clicks=Sum('raw_clicks'),
        conversions=Sum('conversions'),
        earnings=Sum('earning'),
        revenue=Sum('revenue')
    )
    return Response({
        "status": 1,
        "data": total
    })