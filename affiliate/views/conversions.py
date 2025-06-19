#C:\Users\MD BASARULL ISLAM\Downloads\adcpaapi1-main (1)\adcpaapi1-main\affiliate\views\conversions.py

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from tracker.models import Conversion
from offer.models import Offer, Goal, Currency
from django.conf import settings
from datetime import datetime, time, date
import iso8601, pytz
from django.db import models


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ('id', 'title')


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ('name',)


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('code', 'name')


class ConversionSerializer(serializers.ModelSerializer):
    offer = OfferSerializer(source='goal.offer')
    goal = GoalSerializer()
    currency = CurrencySerializer(source='currency', allow_null=True)
    id = serializers.SerializerMethodField()
    click_id = serializers.SerializerMethodField()
    ip = serializers.CharField(read_only=True)  # ← এই লাইনটি যুক্ত করুন

    def get_id(self, obj):
        return str(obj.id)

    def get_click_id(self, obj):
        return str(obj.click.id) if obj.click else None

    class Meta:
        model = Conversion
        fields = (
            'id',
            'created_at',
            'click_id',
            'offer',
            'goal',
            'revenue',
            'payout',
            'status',
            'currency',
            'sub1', 'sub2', 'sub3', 'sub4', 'sub5',
            'country', 'ip', 'ua', 'comment',
        )
class ConversionListView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ConversionSerializer

    def get(self, request):
        params = request.query_params
        tz = pytz.timezone(settings.TIME_ZONE)

        start_date_arg = params.get('start_date')
        end_date_arg = params.get('end_date')

        start_date = iso8601.parse_date(start_date_arg) if start_date_arg else date.today()
        end_date = iso8601.parse_date(end_date_arg) if end_date_arg else date.today()

        start_datetime = tz.localize(datetime.combine(start_date, time.min))
        end_datetime = tz.localize(datetime.combine(end_date, time.max))

        filters = {
            'created_at__range': [start_datetime, end_datetime],
            'click__affiliate_id': request.user.id,
        }

        if params.get('offer_id'):
            filters['goal__offer_id'] = params.get('offer_id')

        if params.get('status'):
            filters['status'] = params.get('status')

        if params.get('transaction_id'):
            filters['transaction_id'] = params.get('transaction_id')

        if params.get('click_id'):
            filters['click__id'] = params.get('click_id')

        queryset = Conversion.objects.filter(**filters).order_by('-created_at')

        if params.get('summary') == 'true':
            total_revenue = queryset.aggregate(total=models.Sum('revenue'))['total'] or 0.0
            total_payout = queryset.aggregate(total=models.Sum('payout'))['total'] or 0.0
            count = queryset.count()
            return Response({
                'total_conversions': count,
                'total_revenue': round(total_revenue, 2),
                'total_payout': round(total_payout, 2),
                'profit': round(total_revenue - total_payout, 2),
            })

        try:
            limit = int(params.get('limit', 50))
            offset = int(params.get('offset', 0))
        except ValueError:
            return Response({"detail": "limit and offset must be integers"}, status=status.HTTP_400_BAD_REQUEST)

        paginated_qs = queryset[offset:offset+limit]
        serialized = ConversionSerializer(paginated_qs, many=True)

        return Response({
            'count': queryset.count(),
            'limit': limit,
            'offset': offset,
            'results': serialized.data
        })
