from rest_framework import generics, permissions
from tracker.models import Conversion
from userpanel.serializers.conversion import ConversionSerializer


class ConversionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ConversionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # ✅ শুধু নিজের conversion গুলো দেখতে পারবে
        return Conversion.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # ✅ Conversion create করলে ইউজার নিজে সেট হবে
        serializer.save(user=self.request.user)
