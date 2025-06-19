from rest_framework import viewsets, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from offer.models import Offer
from userpanel.models import OfferTrafficSource
from userpanel.serializers.offer import OfferListSerializer
from userpanel.serializers.offer_traffic_source import OfferTrafficSourceSerializer


class OfferListAPIView(ListAPIView):
    """
    Authenticated users can view all active offers.
    """
    queryset = Offer.objects.filter(status='active')
    serializer_class = OfferListSerializer
    permission_classes = [permissions.IsAuthenticated]


class OfferTrackingAPIView(RetrieveAPIView):
    """
    Returns the tracking URL for an offer with user's affiliate ID appended.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Offer.objects.filter(status='active')

    def retrieve(self, request, *args, **kwargs):
        offer = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))

        # Build tracking URL
        aff_id = request.user.id
        base_url = offer.tracking_url or ""
        separator = "&" if "?" in base_url else "?"
        tracking_url = f"{base_url}{separator}aff_id={aff_id}"

        return Response({
            "offer_id": offer.id,
            "title": offer.title,
            "tracking_url": tracking_url
        })


class OfferTrafficSourceViewSet(viewsets.ModelViewSet):
    """
    CRUD for user's traffic sources per offer.
    """
    queryset = OfferTrafficSource.objects.all()
    serializer_class = OfferTrafficSourceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)