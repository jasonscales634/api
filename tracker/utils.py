from datetime import datetime
from typing import Optional
from django.http import HttpRequest
from tracker.models import Conversion, conversion_statuses, Click
import httpagentparser
import csv
import io
from geolite2 import geolite2
import pytz
from functools import lru_cache

# GeoIP reader ইনিশিয়ালাইজেশন (মেমরিতে ক্যাশিং এর জন্য global)
_geo_reader = geolite2.reader()

def filter_conversions(queryset, start_date: Optional[str], end_date: Optional[str], status: Optional[str]):
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            queryset = queryset.filter(created_at__date__gte=start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            queryset = queryset.filter(created_at__date__lte=end)
        except ValueError:
            pass

    if status and status in dict(conversion_statuses):
        queryset = queryset.filter(status=status)

    return queryset

def paginate_queryset(queryset, limit: Optional[int], offset: Optional[int]):
    if offset is not None:
        queryset = queryset[int(offset):]
    if limit is not None:
        queryset = queryset[:int(limit)]
    return queryset

def export_conversions_to_csv(conversions_queryset):
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    writer.writerow([
        'ID', 'Created At', 'Click ID', 'Click Date',
        'Sub1', 'Sub2', 'Sub3', 'Sub4', 'Sub5',
        'IP', 'Country', 'City', 'UA', 'OS', 'Device',
        'Device Time', 'IP Local Time',
        'Goal Value', 'Sum', 'Status', 'Comment',
        'Transaction ID',
        'Revenue', 'Payout',
        'Goal', 'Currency', 'Offer',
        'Affiliate', 'Affiliate Manager'
    ])

    for conv in conversions_queryset:
        writer.writerow([
            conv.id,
            conv.created_at.strftime('%Y-%m-%d %H:%M:%S') if conv.created_at else '',
            conv.click_id,
            conv.click_date.strftime('%Y-%m-%d %H:%M:%S') if conv.click_date else '',
            conv.sub1, conv.sub2, conv.sub3, conv.sub4, conv.sub5,
            conv.ip,
            conv.country or '-',
            conv.city or '-',
            conv.ua,
            conv.os,
            conv.device,
            conv.device_time.strftime('%Y-%m-%d %H:%M:%S') if conv.device_time else '',
            conv.ip_local_time.strftime('%Y-%m-%d %H:%M:%S') if conv.ip_local_time else '',
            conv.goal_value,
            conv.sum,
            conv.status,
            conv.comment,
            conv.transaction_id if conv.transaction_id else str(conv.id),
            conv.revenue,
            conv.payout,
            getattr(conv.goal, 'name', '-'),
            getattr(conv.currency, 'code', '-'),
            getattr(conv.offer, 'title', '-'),
            getattr(conv.affiliate, 'email', '-'),
            getattr(conv.affiliate_manager, 'email', '-'),
        ])

    return output.getvalue()

def get_device_info(user_agent: str) -> dict:
    try:
        parsed = httpagentparser.detect(user_agent)
        device = parsed.get('platform', {}).get('name', 'Unknown')
        os = parsed.get('os', {}).get('name', 'Unknown')
        browser = parsed.get('browser', {}).get('name', 'Unknown')
    except Exception:
        device = os = browser = 'Unknown'

    return {
        'device': device,
        'os': os,
        'browser': browser
    }

@lru_cache(maxsize=1000)
def get_timezone_from_ip(ip: str) -> Optional[str]:
    info = _geo_reader.get(ip)
    if not info:
        return None
    return info.get("location", {}).get("time_zone")

def get_geo_time(ip: str) -> Optional[datetime]:
    tz_name = get_timezone_from_ip(ip)
    if not tz_name:
        return None
    try:
        tz = pytz.timezone(tz_name)
        return datetime.now(tz)
    except Exception:
        return None

def get_geo_city_country(ip: str) -> tuple[Optional[str], Optional[str]]:
    """IP থেকে City এবং Country নাম বের করে দেয়"""
    info = _geo_reader.get(ip)
    if not info:
        return None, None

    city = info.get('city', {}).get('names', {}).get('en')
    country = info.get('country', {}).get('names', {}).get('en')
    return city or '-', country or '-'

def get_client_ip(request: HttpRequest) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR', '')

def is_fraudulent(ip: str, offer_id: int) -> bool:
    today = datetime.now().date()
    return Click.objects.filter(ip=ip, offer_id=offer_id, created_at__date=today).count() > 50

def replace_macro(url: str, context: dict) -> str:
    for key, value in context.items():
        url = url.replace(f'{{{key}}}', str(value or ''))
    return url
