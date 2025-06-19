# analytics/statistics/views/top_offers.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from tracker.models import Conversion
from offer.models import Offer

class TopOffersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # কনভার্সন সংখ্যার ভিত্তিতে টপ 10 অফার খুঁজে বের করি
            top_offers = (
                Conversion.objects
                .values('offer_id')
                .annotate(total_conversions=Count('id'))
                .order_by('-total_conversions')[:10]
            )

            # অফার আইডি লিস্ট তৈরি
            offer_ids = [item['offer_id'] for item in top_offers]

            # অফার নাম গুলো নিয়ে আসি
            offers = Offer.objects.filter(id__in=offer_ids)
            offer_dict = {offer.id: offer.title for offer in offers}

            # কাঠামো বানানো
            results = [
                {
                    "offer_id": item['offer_id'],
                    "offer_name": offer_dict.get(item['offer_id'], 'Unknown'),
                    "conversions": item['total_conversions']
                }
                for item in top_offers
            ]

            return Response({"status": 1, "results": results})

        except Exception as e:
            return Response({
                "status": 0,
                "error": str(e),
                "message": "টপ অফার ডেটা লোড করতে সমস্যা হয়েছে।"
            }, status=500)
