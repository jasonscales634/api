from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
import csv

from tracker.models import Click, Conversion
from tracker.serializers import ClickSerializer, ConversionSerializer
from rest_framework.pagination import LimitOffsetPagination


class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class ClickListAPIView(generics.ListAPIView):
    """Return clicks for the authenticated user (or all for admin)."""
    serializer_class = ClickSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['offer__name', 'ip', 'country', 'city', 'sub1', 'sub2', 'sub3', 'sub4', 'sub5']
    ordering_fields = ['created_at', 'revenue', 'payout']
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['country', 'affiliate', 'city', 'device', 'os', 'sub1', 'sub2', 'sub3', 'sub4', 'sub5']

    def get_queryset(self):
        user = self.request.user
        return Click.objects.all() if user.is_staff else Click.objects.filter(affiliate=user)


class ConversionListAPIView(generics.ListAPIView):
    """Return conversions for the authenticated user (or all for admin)."""
    serializer_class = ConversionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['offer__name', 'ip', 'country', 'goal_value', 'sub1', 'sub2', 'sub3', 'sub4', 'sub5', 'city']
    ordering_fields = ['created_at', 'revenue', 'payout', 'status']
    pagination_class = StandardResultsSetPagination
    filterset_fields = ['status', 'country', 'city', 'device', 'os', 'sub1', 'sub2', 'sub3', 'sub4', 'sub5']

    def get_queryset(self):
        user = self.request.user
        qs = Conversion.objects.all() if user.is_staff else Conversion.objects.filter(affiliate=user)

        # তারিখ দিয়ে ফিল্টার (start_date, end_date)
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            qs = qs.filter(created_at__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__lte=end_date)

        return qs

    def list(self, request, *args, **kwargs):
        export = request.query_params.get('export')
        if export == 'csv':
            qs = self.filter_queryset(self.get_queryset())
            return self.export_as_csv(qs)
        return super().list(request, *args, **kwargs)

    def export_as_csv(self, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="conversions.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Created At', 'Status', 'Sum', 'Goal Value',
            'Affiliate ID', 'Offer ID', 'Payout', 'Revenue',
            'Country', 'City', 'Device', 'OS',
            'Sub1', 'Sub2', 'Sub3', 'Sub4', 'Sub5'
        ])

        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.created_at,
                obj.status,
                obj.sum,
                obj.goal_value,
                obj.affiliate_id,
                obj.offer_id,
                obj.payout,
                obj.revenue,
                obj.country,
                obj.city,
                obj.device,
                obj.os,
                obj.sub1,
                obj.sub2,
                obj.sub3,
                obj.sub4,
                obj.sub5,
            ])

        return response
