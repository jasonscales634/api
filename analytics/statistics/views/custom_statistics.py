from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from analytics.statistics.models.statistics import DailyStat
from analytics.statistics.serializers.custom_statistics import CustomStatisticsSerializer
from api.pagination import StandardResultsSetPagination
from django.db.models import Sum
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta, date


class CustomStatisticsAPIView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)
    serializer_class = CustomStatisticsSerializer

    def get(self, request):
        user = request.user
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        default_used = False
        if start_date_str and end_date_str:
            start_date = parse_date(start_date_str)
            end_date = parse_date(end_date_str)
        else:
            default_used = True
            end_date = date.today()
            if user.is_staff:
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=7)

        country = request.GET.get("country")
        affiliate_id = request.GET.get("affiliate")

        queryset = DailyStat.objects.filter(date__range=[start_date, end_date])
        if country:
            queryset = queryset.filter(country=country)
        if affiliate_id:
            queryset = queryset.filter(affiliate_id=affiliate_id)

        stats_queryset = queryset.values("date").annotate(
            impressions=Sum("raw_clicks"),
            clicks=Sum("unique_clicks"),
            conversions=Sum("conversions"),
            revenue=Sum("revenue"),
            payout=Sum("charge"),
        ).order_by("date")

        paginator = StandardResultsSetPagination()
        paginated_stats = paginator.paginate_queryset(stats_queryset, request, view=self)

        formatted = []
        for stat in paginated_stats:
            epc = (stat["revenue"] / stat["clicks"]) if stat["clicks"] else 0.0
            cr = (stat["conversions"] / stat["clicks"] * 100) if stat["clicks"] else 0.0
            formatted.append({
                "date": stat["date"],
                "impressions": stat["impressions"],
                "clicks": stat["clicks"],
                "conversions": stat["conversions"],
                "revenue": stat["revenue"],
                "payout": stat["payout"],
                "epc": round(epc, 2),
                "cr": round(cr, 2),
            })

        serializer = self.serializer_class(formatted, many=True)
        return Response({
            "status": 1,
            "stats": serializer.data,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "default_used": default_used
            },
            "pagination": {
                "per_page": paginator.page.paginator.per_page,
                "total_count": paginator.page.paginator.count,
                "page": paginator.page.number
            }
        })