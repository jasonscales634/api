from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count, Sum
from analytics.statistics.models.statistics import DailyStat
from tracker.models import Conversion


class AffiliateStatsAPIView(APIView):
    def get(self, request):
        stats = (
            Conversion.objects
            .values('click__affiliate_id')
            .annotate(
                total_conversions=Count('id'),
                total_revenue=Sum('revenue'),
                total_clicks=Count('click')
            )
            .order_by('-total_revenue')
        )
        return Response({"status": 1, "results": stats})


class DailyAffiliateStatsView(APIView):
    def get(self, request):
        stats = (
            DailyStat.objects
            .values('date', 'affiliate_id')
            .annotate(
                total_clicks=Sum('raw_clicks'),
                total_uniques=Sum('unique_clicks'),
                total_conversions=Sum('conversions'),
                total_revenue=Sum('revenue'),
                total_earning=Sum('earning'),
            )
            .order_by('-date')
        )
        return Response({"status": 1, "results": stats})