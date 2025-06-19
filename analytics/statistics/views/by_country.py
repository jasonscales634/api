# analytics/statistics/views/by_country.py

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum

from analytics.statistics.models.country import Country  # ✅ ঠিক করা import
from analytics.serializers.country import CountrySerializer
from analytics.statistics.models.statistics import DailyStat


# 🔹 Country list endpoint
class CountryListAPIView(APIView):
    def get(self, request):
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data)


# 🔹 Country-wise analytics breakdown
class CountryBreakdownAPIView(APIView):
    def get(self, request):
        stats = (
            DailyStat.objects.values('country')
            .annotate(
                raw_clicks=Sum('raw_clicks'),
                unique_clicks=Sum('unique_clicks'),
                conversions=Sum('conversions'),
                revenue=Sum('revenue'),
                earning=Sum('earning')
            )
            .order_by('-revenue')
        )

        return Response({
            "status": 1,
            "results": stats
        })