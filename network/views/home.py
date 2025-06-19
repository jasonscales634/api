# network/views/home.py (✅ updated for drf-spectacular)
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema

@extend_schema_view(
    get=extend_schema(
        summary="Network API Root",
        description="Returns available endpoints for network admin"
    )
)
class NetworkRootAPIView(APIView):
    def get(self, request):
        return Response({
            "message": "Welcome to the Network (Admin) API Root",
            "endpoints": {
                "affiliates": "/network/affiliates/",
                "offers": "/network/offers/",
                "conversions": "/network/conversions/",
                "stats": {
                    "daily": "/network/stats/daily/",
                    "offers": "/network/stats/offers/",
                    "affiliates": "/network/stats/affiliates/"
                }
            }
        })