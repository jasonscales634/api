# affiliate/views/dashboard.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class AffiliateDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # তোমার পছন্দমতো ডাটা পাঠাও এখানে
        manager_info = {
            "manager_name": "John Doe",
            "manager_email": "john@example.com",
            "skype": "john.doe",
            "telegram": "@johndoe"
        }
        return Response(manager_info)
