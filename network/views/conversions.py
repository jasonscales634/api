# network/views/conversions.py

import iso8601
import pytz
from datetime import datetime, time, date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import serializers

from tracker.models import Conversion
from offer.models import Offer  # ✅ Fixed import
from django.conf import settings


class ConversionListSerializer(serializers.ModelSerializer):
    offer_title = serializers.SerializerMethodField()

    class Meta:
        model = Conversion
        fields = (
            'id',
            'created_at',
            'offer_id',
            'offer_title',  # ✅ newly added field
            'revenue',
            'payout',
            'sub1',
            'sub2',
            'sub3',
            'sub4',
            'sub5',
            'status',
            'goal',
            'goal_value',
            'country',
            'ip',
            'ua',
        )

    def get_offer_title(self, obj):
        return obj.offer.title if obj.offer else None


class ConversionListView(APIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    def get(self, request):
        start_date_arg = request.query_params.get('start_date')
        end_date_arg = request.query_params.get('end_date')
        offer_id = request.query_params.get('offer_id')

        if start_date_arg:
            start_date = iso8601.parse_date(start_date_arg).date()
        else:
            start_date = date.today()

        if end_date_arg:
            end_date = iso8601.parse_date(end_date_arg).date()
        else:
            end_date = date.today()

        tz = pytz.timezone(settings.TIME_ZONE)
        start_datetime = tz.localize(datetime.combine(start_date, time.min))
        end_datetime = tz.localize(datetime.combine(end_date, time.max))

        filters = {
            'created_at__range': [start_datetime, end_datetime],
            'affiliate_id': request.user.id,
        }

        if offer_id:
            filters['offer_id'] = offer_id

        queryset = Conversion.objects.select_related('offer').filter(**filters).order_by('-created_at')
        serializer = ConversionListSerializer(queryset, many=True)
        return Response(serializer.data)