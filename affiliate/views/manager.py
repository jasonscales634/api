from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

class ManagerInfoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "manager_name": "John Doe",
            "manager_email": "john@example.com",
            "telegram": "johndoe"
        })
