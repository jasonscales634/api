from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from offer.models import Offer
from tracker.models import Click, Conversion

from django.utils import timezone
from django.db.models import Count, Sum
from datetime import datetime

class OffersBreakdownView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=401)

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        try:
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            else:
                start_date = timezone.now().replace(hour=0, minute=0, second=0)

            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            else:
                end_date = timezone.now()
        except Exception as e:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        offers = Offer.objects.filter(status="active")

        data = []
        for offer in offers:
            clicks = Click.objects.filter(offer=offer, created_at__range=(start_date, end_date))
            conversions = Conversion.objects.filter(offer=offer, created_at__range=(start_date, end_date))

            raw_clicks = clicks.count()
            unique_clicks = clicks.values("ip_address").distinct().count()
            conv_count = conversions.count()
            total_revenue = conversions.aggregate(total=Sum("revenue"))["total"] or 0
            total_earning = conversions.aggregate(total=Sum("payout"))["total"] or 0

            data.append({
                "offer_id": offer.id,
                "offer_title": offer.title,
                "raw_clicks": raw_clicks,
                "unique_clicks": unique_clicks,
                "conversions": conv_count,
                "revenue": float(total_revenue),
                "earning": float(total_earning),
                "status": offer.status,
            })

        return Response(data)