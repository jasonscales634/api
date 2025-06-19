from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from analytics.statistics.models.statistics import DailyStat
from django.utils import timezone
from datetime import timedelta

@api_view(['GET'])
def statistics_last_30_days(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=30)

    queryset = DailyStat.objects.filter(date__range=(start_date, today))
    data = queryset.values('date').order_by('date').annotate(
        clicks=Sum('raw_clicks'),
        conversions=Sum('conversions'),
        earnings=Sum('earning'),
        revenue=Sum('revenue')
    )
    return Response({"status": 1, "results": list(data)})
