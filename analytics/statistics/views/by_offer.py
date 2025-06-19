from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from analytics.statistics.models.statistics import DailyStat
from offer.models import Offer
from analytics.statistics.serializers.by_offer import OfferBreakdownSerializer

class OfferBreakdownAPIView(APIView):
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        stats = DailyStat.objects.all()
        if start_date and end_date:
            stats = stats.filter(date__range=[start_date, end_date])

        data = stats.values('offer', 'offer__title').annotate(
            raw_clicks=Sum('raw_clicks'),
            unique_clicks=Sum('unique_clicks'),
            conversions=Sum('conversions'),
            revenue=Sum('revenue'),
            earning=Sum('earning'),
        ).order_by('-revenue')

        formatted_data = []
        offer_ids_with_stats = set()

        for d in data:
            offer_ids_with_stats.add(str(d['offer']))
            formatted_data.append({
                "offer_id": str(d['offer']),
                "offer_title": d['offer__title'],
                "raw_clicks": d['raw_clicks'] or 0,
                "unique_clicks": d['unique_clicks'] or 0,
                "conversions": d['conversions'] or 0,
                "revenue": float(d['revenue'] or 0),
                "earning": float(d['earning'] or 0),
            })

        all_active_offers = Offer.objects.filter(status='active', is_deleted=False)
        for offer in all_active_offers:
            if str(offer.id) not in offer_ids_with_stats:
                formatted_data.append({
                    "offer_id": str(offer.id),
                    "offer_title": offer.title,
                    "raw_clicks": 0,
                    "unique_clicks": 0,
                    "conversions": 0,
                    "revenue": 0.0,
                    "earning": 0.0,
                })

        serializer = OfferBreakdownSerializer(formatted_data, many=True)
        return Response({
            "status": 1,
            "results": serializer.data
        })