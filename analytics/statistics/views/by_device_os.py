# analytics/statistics/views/by_device_os.py

from rest_framework.views import APIView
from rest_framework.response import Response
from analytics.statistics.models.statistics import DailyStat
from django.db.models import Sum

class DeviceBreakdownAPIView(APIView):
    def get(self, request):
        stats = DailyStat.objects.values('device').annotate(
            clicks=Sum('raw_clicks'),
            conversions=Sum('conversions'),
            revenue=Sum('revenue'),
            earning=Sum('earning')
        ).order_by('-revenue')
        return Response({"status": 1, "results": stats})

class OSBreakdownAPIView(APIView):
    def get(self, request):
        stats = DailyStat.objects.values('os').annotate(
            clicks=Sum('raw_clicks'),
            conversions=Sum('conversions'),
            revenue=Sum('revenue'),
            earning=Sum('earning')
        ).order_by('-revenue')
        return Response({"status": 1, "results": stats})
