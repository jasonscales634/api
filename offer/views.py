from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Offer, Landing
from .serializers import OfferSerializer, LandingSerializer
from .permissions import IsAdminOrReadOnly
from offer.cache_offers import TrackerCache  # Uncomment if needed
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required



class OfferViewSet(viewsets.ModelViewSet):
    serializer_class = OfferSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.is_superuser:
            # Admin: সব offer (active + paused), excluding soft-deleted
            return Offer.objects.filter(is_deleted=False).order_by('-created_at') \
                .prefetch_related("goals", "landings")

        # Affiliate: Active & Assigned Offers only
        return Offer.objects.filter(
            is_deleted=False,
            status="active",
            affiliates=user
        ).order_by('-created_at').prefetch_related("goals", "landings")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user.is_staff or request.user.is_superuser:
            return super().retrieve(request, *args, **kwargs)

        if request.user in instance.affiliates.all():
            return super().retrieve(request, *args, **kwargs)

        return Response({"detail": "⛔ You do not have permission to view this offer."}, status=403)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """✅ Soft Delete an Offer instead of permanent delete"""
        instance = self.get_object()
        instance.is_deleted = True
        instance.status = 'deleted'
        instance.save()
        return Response({"detail": "✅ Offer has been soft-deleted."}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminOrReadOnly])
    def deleted(self, request):
        """🔍 Admin-only: List all soft-deleted offers"""
        if not request.user.is_staff:
            return Response({"detail": "⛔ Not allowed."}, status=403)
        queryset = Offer.objects.filter(is_deleted=True).order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminOrReadOnly])
    def restore(self, request, pk=None):
        """♻️ Restore a soft-deleted offer"""
        offer = self.get_object()
        if not offer.is_deleted:
            return Response({"detail": "⚠️ Offer is not deleted."}, status=400)
        offer.is_deleted = False
        offer.status = "active"
        offer.save()
        return Response({"detail": "✅ Offer has been restored."})


class LandingListCreateView(generics.ListCreateAPIView):
    serializer_class = LandingSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Landing.objects.filter(offer_id=self.kwargs['offer_id'])

    def perform_create(self, serializer):
        offer = get_object_or_404(Offer, id=self.kwargs['offer_id'])
        serializer.save(offer=offer)


class LandingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LandingSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Landing.objects.filter(offer_id=self.kwargs['offer_id'])



@api_view(['GET'])
def top_offers(request):
    # উদাহরণস্বরূপ ডাটা (পরে ডাটাবেজ থেকে আনতে পারবেন)
    data = {
        "offers": [
            {"id": 1, "title": "Top Offer 1"},
            {"id": 2, "title": "Top Offer 2"},
        ]
    }
    return Response(data)


@staff_member_required
def clone_offer_view(request, pk):
    offer = get_object_or_404(Offer, pk=pk)
    offer.pk = None  # নতুন অফার তৈরি
    offer.title += ' (Cloned)'
    offer.save()
    return redirect('/admin/offer/offer/')
