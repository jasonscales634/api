#C:\Users\MD BASARULL ISLAM\Downloads\adcpaapi1-main (1)\adcpaapi1-main\affiliate\views\stats.py

import iso8601
from datetime import datetime, time, timedelta, date
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from tracker.models import Click, Conversion
from django.db.models import Sum

from ..dao import daily_report, offer_report, goal_report, report_bysub


@extend_schema(
    tags=["Affiliate - Stats"],
    summary="Get daily stats",
    description="Returns daily click, conversion, and earning statistics for the authenticated affiliate. You can optionally filter by offer and date range (start_date, end_date)."
)
class DailyStatsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        start_date_arg = request.query_params.get('start_date')
        end_date_arg = request.query_params.get('end_date')
        offer_id = request.query_params.get('offer_id')

        if start_date_arg:
            start_date = iso8601.parse_date(start_date_arg)
        else:
            start_date = date.today() - timedelta(days=6)

        if end_date_arg:
            end_date = iso8601.parse_date(end_date_arg)
        else:
            end_date = date.today()

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        data = daily_report(request.user.id, start_datetime, end_datetime, offer_id)
        return Response(data)


@extend_schema(
    tags=["Affiliate - Stats"],
    summary="Get offer-wise stats",
    description="Returns aggregated stats grouped by offers for the authenticated affiliate. Accepts optional start_date and end_date query parameters."
)
class OffersStatsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        start_date_arg = request.query_params.get('start_date')
        end_date_arg = request.query_params.get('end_date')

        if start_date_arg:
            start_date = iso8601.parse_date(start_date_arg)
        else:
            start_date = date.today() - timedelta(days=6)

        if end_date_arg:
            end_date = iso8601.parse_date(end_date_arg)
        else:
            end_date = date.today()

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        data = offer_report(request.user.id, start_datetime, end_datetime)
        return Response(data)


@extend_schema(
    tags=["Affiliate - Stats"],
    summary="Get goal-wise stats",
    description="Returns stats grouped by goals for the authenticated affiliate. Accepts optional start_date and end_date."
)
class GoalStatsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        start_date_arg = request.query_params.get('start_date')
        end_date_arg = request.query_params.get('end_date')

        if start_date_arg:
            start_date = iso8601.parse_date(start_date_arg)
        else:
            start_date = date.today() - timedelta(days=6)

        if end_date_arg:
            end_date = iso8601.parse_date(end_date_arg)
        else:
            end_date = date.today()

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        data = goal_report(request.user.id, start_datetime, end_datetime)
        return Response(data)


@extend_schema(
    tags=["Affiliate - Stats"],
    summary="Get stats by sub ID",
    description="Returns stats filtered by sub1 to sub5 for a specific offer. Requires `offer_id` as query param and sub in [1,2,3,4,5] as path param."
)
class SubStatsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, sub):
        if sub not in range(1, 6):
            return Response(status.HTTP_404_NOT_FOUND)

        offer_id = request.query_params.get('offer_id')
        if not offer_id:
            return Response(
                {'message': 'offer must be specified'},
                status.HTTP_400_BAD_REQUEST
            )

        start_date_arg = request.query_params.get('start_date')
        end_date_arg = request.query_params.get('end_date')

        if start_date_arg:
            start_date = iso8601.parse_date(start_date_arg)
        else:
            start_date = date.today() - timedelta(days=6)

        if end_date_arg:
            end_date = iso8601.parse_date(end_date_arg)
        else:
            end_date = date.today()

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)

        data = report_bysub(sub, offer_id, request.user.id, start_datetime, end_datetime)
        return Response(data)



@extend_schema(
    tags=["Affiliate - Stats"],
    summary="Affiliate dashboard overview stats",
    description="Returns today's total clicks, conversions, and earnings."
)
class OverviewStatsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        today = date.today()

        clicks = Click.objects.filter(affiliate=user, created_at__date=today).count()
        conversions = Conversion.objects.filter(affiliate=user, created_at__date=today).count()
        earnings = Conversion.objects.filter(affiliate=user, created_at__date=today).aggregate(
            total=Sum('payout'))['total'] or 0

        return Response({
            "clicks": clicks,
            "conversions": conversions,
            "earnings": float(earnings),
        })
