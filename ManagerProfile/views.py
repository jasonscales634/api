from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import AffiliateProfile
from .serializers import AffiliateDashboardSerializer

class AffiliateDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            affiliate = AffiliateProfile.objects.get(user=request.user)
            serializer = AffiliateDashboardSerializer(affiliate)
            return Response(serializer.data)
        except AffiliateProfile.DoesNotExist:
            return Response({"detail": "Affiliate profile not found."}, status=404)
