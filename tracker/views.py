# tracker/views.py (Super Optimized with City support)

import uuid
import csv
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import redirect
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate

from rest_framework import generics, permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from tracker.models import Conversion, conversion_statuses, Click
from tracker.serializers import ConversionSerializer, ClickSerializer
from tracker.utils import get_client_ip, is_fraudulent, replace_macro
from tracker.tasks.click import click as click_task
from tracker.tasks.conversion import conversion
from offer.cache_offers import TrackerCache
from offer.models import Offer

logger = logging.getLogger(__name__)


# --- Core Trackers ---
def legacy_click_redirect(request: HttpRequest) -> HttpResponse:
    return redirect(f"/track/?{request.META.get('QUERY_STRING', '')}")


def track_click(request: HttpRequest) -> HttpResponse:
    offer_id = request.GET.get("offer_id")
    pid = request.GET.get("pid")
    sub_ids = [request.GET.get(f"sub{i}", "") for i in range(1, 6)]
    fb_id = request.GET.get("fb_id", "")
    device_time_raw = request.GET.get("device_time", "")

    if not offer_id or not pid:
        return HttpResponse("❌ Missing offer_id and pid", status=400)

    try:
        offer_obj = Offer.objects.get(id=offer_id, status="active")
    except Offer.DoesNotExist:
        return HttpResponse("❌ Offer not found", status=404)

    if offer_obj.is_capped():
        return HttpResponse("❌ Offer cap reached for today", status=403)

    ip_address = get_client_ip(request)
    if is_fraudulent(ip_address, offer_id):
        logger.warning(f"⚠ Suspicious activity from IP: {ip_address}")
        return HttpResponse("❌ Suspicious activity detected", status=429)

    click_id = uuid.uuid4()
    user_agent = request.META.get("HTTP_USER_AGENT", "")
    device_time = parse_datetime(device_time_raw) if device_time_raw else None

    Click.objects.create(
        id=click_id,
        offer=offer_obj,
        affiliate_id=pid,
        ip=ip_address,
        ua=user_agent,
        sub1=sub_ids[0], sub2=sub_ids[1], sub3=sub_ids[2], sub4=sub_ids[3], sub5=sub_ids[4],
        device_time=device_time,
        country=request.META.get("HTTP_CF_IPCOUNTRY", ""),
        host=request.get_host(),
    )

    context = {
        "click_id": str(click_id),
        "pid": pid,
        "fb_id": fb_id,
        **{f"sub{i+1}": sub_ids[i] for i in range(5)}
    }

    tracking_template = TrackerCache.get_offer(offer_id).get("tracking_link") or settings.DEFAULT_TRACKING_TEMPLATE
    redirect_url = replace_macro(tracking_template, context)

    if not redirect_url.startswith("http"):
        return HttpResponse("❌ Invalid redirect URL", status=400)

    logger.info(f"✅ Redirecting to: {redirect_url}")
    return redirect(redirect_url)


def postback(request: HttpRequest) -> HttpResponse:
    click_id = request.GET.get("click_id")
    goal = request.GET.get("goal", "1")
    status_param = request.GET.get("status")
    sum_param = request.GET.get("sum", "0")

    if not click_id:
        return HttpResponse("❌ Missing click_id", status=400)

    try:
        sum_ = float(sum_param)
    except ValueError:
        sum_ = 0.0

    data = {"click_id": click_id, "goal": goal, "sum": sum_}
    if status_param in dict(conversion_statuses):
        data["status"] = status_param

    conversion.delay(data)
    return HttpResponse("✅ Conversion logged")


def debug_click_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse({
        "ip": get_client_ip(request),
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "host": request.get_host(),
        "full_url": request.build_absolute_uri(),
        "headers": dict(request.headers),
        "GET_params": request.GET.dict()
    }, json_dumps_params={"indent": 2})


# --- Stats APIs ---
class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class ConversionListView(generics.ListAPIView):
    serializer_class = ConversionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Conversion.objects.all()
        q = self.request.query_params
        if q.get("start_date"):
            qs = qs.filter(created_at__date__gte=q["start_date"])
        if q.get("end_date"):
            qs = qs.filter(created_at__date__lte=q["end_date"])
        if q.get("status") in dict(conversion_statuses):
            qs = qs.filter(status=q["status"])
        return qs.order_by("-created_at")

    def list(self, request, *args, **kwargs):
        if request.query_params.get("export") == "csv":
            return self.export_as_csv(self.filter_queryset(self.get_queryset()))
        return super().list(request, *args, **kwargs)

    def export_as_csv(self, qs):
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="conversions.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Created At', 'Click ID', 'Click Date',
            'Sub1', 'Sub2', 'Sub3', 'Sub4', 'Sub5',
            'IP', 'Country', 'City', 'UA', 'OS', 'Device',
            'Device Time', 'IP Local Time',
            'Goal Value', 'Sum', 'Status', 'Comment',
            'Transaction ID', 'Revenue', 'Payout',
            'Goal', 'Currency', 'Offer',
            'Affiliate', 'Affiliate Manager'
        ])
        for c in qs:
            writer.writerow([
                c.id, c.created_at, c.click_id, c.click_date,
                c.sub1, c.sub2, c.sub3, c.sub4, c.sub5,
                c.ip, c.country, c.city, c.ua, c.os, c.device,
                c.device_time, c.ip_local_time,
                c.goal_value, c.sum, c.status, c.comment,
                c.transaction_id or str(c.id),
                c.revenue, c.payout,
                getattr(c.goal, 'name', '-'),
                getattr(c.currency, 'code', '-'),
                getattr(c.offer, 'title', '-'),
                getattr(c.affiliate, 'email', '-'),
                getattr(c.affiliate_manager, 'email', '-')
            ])
        return response


class MyClickListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clicks = Click.objects.filter(affiliate=request.user).order_by('-created_at')[:100]
        return Response({"status": 1, "clicks": ClickSerializer(clicks, many=True).data})


class DashboardSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        clicks = Click.objects.filter(affiliate=request.user, created_at__date=today)
        conversions = Conversion.objects.filter(affiliate=request.user, created_at__date=today)
        hosts = clicks.values('ip', 'host').distinct().count()
        return Response({
            "clicks": clicks.count(),
            "conversions": conversions.count(),
            "hosts": hosts
        })


class AffiliateLiveStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()
        days = [today - timedelta(days=i) for i in range(9, -1, -1)]

        clicks = Click.objects.filter(affiliate=user, created_at__date__range=(days[0], today))
        conversions = Conversion.objects.filter(affiliate=user, created_at__date__range=(days[0], today))

        result_map = {str(d): {"clicks": 0, "hosts": 0, "conversions": 0, "earnings": 0.0} for d in days}

        for row in clicks.annotate(date=TruncDate('created_at')).values('date').annotate(clicks=Count('id')):
            result_map[str(row['date'])]['clicks'] = row['clicks']

        for row in clicks.annotate(date=TruncDate('created_at')).values('date').annotate(hosts=Count('host', distinct=True)):
            result_map[str(row['date'])]['hosts'] = row['hosts']

        for row in conversions.annotate(date=TruncDate('created_at')).values('date').annotate(conversions=Count('id'), earnings=Sum('payout')):
            result_map[str(row['date'])]['conversions'] = row['conversions']
            result_map[str(row['date'])]['earnings'] = float(row['earnings'] or 0)

        return Response({"status": 1, "results": [
            {"date": k, **v} for k, v in sorted(result_map.items())
        ]})
