from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from analytics.statistics.models.statistics import DailyStat

class OSBreakdownAPIView(APIView):
    def get(self, request):
        stats = DailyStat.objects.values('os').annotate(
            raw_clicks=Sum('raw_clicks'),
            unique_clicks=Sum('unique_clicks'),
            conversions=Sum('conversions'),
            revenue=Sum('revenue'),
            earning=Sum('earning')
        ).order_by('-revenue')

        return Response({
            "status": 1,
            "results": stats
        })
