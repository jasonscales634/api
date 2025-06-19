from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDate
from user_agents import parse as parse_ua
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from tracker.models import Click, Conversion
from tracker.statistics.serializers import ConversionSerializer
from pytz import timezone as pytz_timezone
from tracker.models import Click, Conversion, APPROVED_STATUS


class DailyStatAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        from_str = request.GET.get("from")
        to_str = request.GET.get("to")
        try:
            from_date = parse_date(from_str) if from_str else today - timedelta(days=6)
            to_date = parse_date(to_str) if to_str else today
        except:
            return Response({"status": 0, "message": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        clicks_qs = Click.objects.filter(
            affiliate=user,
            created_at__date__range=(from_date, to_date)
        ).annotate(date=TruncDate("created_at")).values("date").annotate(
            clicks=Count("id"),
            hosts=Count("ip", distinct=True)
        )

        convs_qs = Conversion.objects.filter(
            affiliate=user,
            created_at__date__range=(from_date, to_date)
        ).annotate(date=TruncDate("created_at")).values("date").annotate(
            conversions=Count("id"),
            earnings=Sum("payout")
        )

        click_map = {i["date"]: i for i in clicks_qs}
        conv_map = {i["date"]: i for i in convs_qs}

        results = []
        for i in range((to_date - from_date).days + 1):
            day = from_date + timedelta(days=i)
            results.append({
                "date": day.strftime("%Y-%m-%d"),
                "hosts": click_map.get(day, {}).get("hosts", 0),
                "clicks": click_map.get(day, {}).get("clicks", 0),
                "conversions": conv_map.get(day, {}).get("conversions", 0),
                "earnings": float(conv_map.get(day, {}).get("earnings") or 0),
            })

        return Response({"status": 1, "results": results})


# ✅ 2. Conversion Report API
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def conversion_report_latest(request):
    user = request.user
    qs = Conversion.objects.filter(affiliate=user)

    from_str = request.GET.get("from")
    to_str = request.GET.get("to")
    tz_name = request.GET.get("timezone", "UTC")
    country = request.GET.get("country", "").strip()
    sub_search = request.GET.get("sub_search", "").strip()

    try:
        if from_str and to_str:
            tz_obj = pytz_timezone(tz_name)
            from_date = parse_date(from_str)
            to_date = parse_date(to_str)

            if from_date and to_date:
                from_dt = make_aware(datetime.combine(from_date, datetime.min.time())).astimezone(tz_obj)
                to_dt = make_aware(datetime.combine(to_date, datetime.max.time())).astimezone(tz_obj)
                qs = qs.filter(created_at__range=(from_dt, to_dt))
    except Exception as e:
        print("❌ Date parse error:", e)

    if country:
        qs = qs.filter(country__iexact=country)

    if sub_search:
        qs = qs.filter(
            Q(sub1__icontains=sub_search) |
            Q(sub2__icontains=sub_search) |
            Q(sub3__icontains=sub_search) |
            Q(sub4__icontains=sub_search) |
            Q(sub5__icontains=sub_search)
        )

    qs = qs.order_by("-created_at")[:200]
    serializer = ConversionSerializer(qs, many=True)
    return Response({"status": 1, "results": serializer.data})


# ✅ 3. Offer Breakdown API
class AffiliateOfferBreakdownAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        from_str = request.GET.get("from")
        to_str = request.GET.get("to")
        tz_name = request.GET.get("timezone", "America/New_York")
        country = request.GET.get("country", "").strip()

        try:
            tz_obj = pytz_timezone(tz_name)
            from_date = parse_date(from_str)
            to_date = parse_date(to_str)

            if not from_date or not to_date:
                raise ValueError("Missing or invalid dates.")

            from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
            to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))

        except Exception as e:
            return Response({"status": 0, "message": f"Invalid date or timezone: {e}"}, status=400)

        # ✅ All Clicks (global)
        clicks_qs = Click.objects.filter(created_at__range=(from_dt, to_dt))
        if country:
            clicks_qs = clicks_qs.filter(country__iexact=country)

        clicks = clicks_qs.values("offer_id", "offer__title").annotate(
            hosts=Count("ip", distinct=True),
            clicks=Count("id")
        )

        # ✅ Only Conversions for this user
        conversions_qs = Conversion.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt),
            status="approved"
        )
        if country:
            conversions_qs = conversions_qs.filter(country__iexact=country)

        conversions = conversions_qs.values("offer_id").annotate(
            approved=Count("id"),
            total=Sum("payout")
        )

        # Mapping
        click_map = {c["offer_id"]: c for c in clicks}
        conv_map = {c["offer_id"]: c for c in conversions}

        # Result merging
        results = []
        for offer_id, c in click_map.items():
            conv = conv_map.get(offer_id, {"approved": 0, "total": 0})
            results.append({
                "offer_id": offer_id,
                "offer_title": c["offer__title"],
                "hosts": c["hosts"],
                "clicks": c["clicks"],
                "approved": conv["approved"],
                "total": float(conv["total"] or 0),
            })

        return Response({"status": 1, "results": results})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def browser_breakdown(request):
    user = request.user
    from_str = request.GET.get("from")
    to_str = request.GET.get("to")
    tz_name = request.GET.get("timezone", "America/New_York")
    country = request.GET.get("country", "").strip()

    try:
        tz_obj = pytz_timezone(tz_name)
        from_date = parse_date(from_str)
        to_date = parse_date(to_str)

        from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
        to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
    except:
        return Response({"status": 0, "message": "Invalid date format"}, status=400)

    clicks_qs = Click.objects.filter(
        affiliate=user,
        created_at__range=(from_dt, to_dt)
    )
    if country:
        clicks_qs = clicks_qs.filter(country__iexact=country)

    # ✅ loop করে browser detect করা হচ্ছে
    browser_map = {}

    for click in clicks_qs:
        browser_str = parse_ua(click.ua).browser.family or "Unknown"

        if browser_str not in browser_map:
            browser_map[browser_str] = {
                "browser": browser_str,
                "hosts_set": set(),
                "clicks": 0,
                "approved": 0,
                "total": 0.0
            }

        item = browser_map[browser_str]
        item["clicks"] += 1
        item["hosts_set"].add(click.ip)

    # ✅ Approved conversion count
    conversions = Conversion.objects.filter(
        affiliate=user,
        created_at__range=(from_dt, to_dt),
        status="approved"
    )
    if country:
        conversions = conversions.filter(country__iexact=country)

    for conv in conversions:
        browser_str = parse_ua(conv.ua).browser.family or "Unknown"
        if browser_str in browser_map:
            browser_map[browser_str]["approved"] += 1
            browser_map[browser_str]["total"] += float(conv.payout or 0)

    # ✅ Final data
    results = []
    for val in browser_map.values():
        results.append({
            "browser": val["browser"],
            "hosts": len(val["hosts_set"]),
            "clicks": val["clicks"],
            "approved": val["approved"],
            "total": round(val["total"], 2)
        })

    return Response({"status": 1, "results": results})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def os_breakdown(request):
    user = request.user
    from_str = request.GET.get("from")
    to_str = request.GET.get("to")
    tz_name = request.GET.get("timezone", "America/New_York")
    country = request.GET.get("country", "").strip()

    try:
        tz_obj = pytz_timezone(tz_name)
        from_date = parse_date(from_str)
        to_date = parse_date(to_str)
        from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
        to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
    except:
        return Response({"status": 0, "message": "Invalid date format"}, status=400)

    # ✅ All Clicks by user
    clicks_qs = Click.objects.filter(
        affiliate=user,
        created_at__range=(from_dt, to_dt)
    )
    if country:
        clicks_qs = clicks_qs.filter(country__iexact=country)

    os_map = {}

    for click in clicks_qs:
        os_str = parse_ua(click.ua).os.family or "Unknown"
        if os_str not in os_map:
            os_map[os_str] = {
                "os": os_str,
                "hosts_set": set(),
                "clicks": 0,
                "approved": 0,
                "total": 0.0
            }

        item = os_map[os_str]
        item["clicks"] += 1
        item["hosts_set"].add(click.ip)

    # ✅ Approved Conversions
    conversions = Conversion.objects.filter(
        affiliate=user,
        created_at__range=(from_dt, to_dt),
        status="approved"
    )
    if country:
        conversions = conversions.filter(country__iexact=country)

    for conv in conversions:
        os_str = parse_ua(conv.ua).os.family or "Unknown"
        if os_str in os_map:
            os_map[os_str]["approved"] += 1
            os_map[os_str]["total"] += float(conv.payout or 0)

    # ✅ Final response
    results = []
    for item in os_map.values():
        results.append({
            "os": item["os"],
            "hosts": len(item["hosts_set"]),
            "clicks": item["clicks"],
            "approved": item["approved"],
            "total": round(item["total"], 2)
        })

    return Response({"status": 1, "results": results})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def device_breakdown(request):
    user = request.user
    from_str = request.GET.get("from")
    to_str = request.GET.get("to")
    tz_name = request.GET.get("timezone", "America/New_York")
    country = request.GET.get("country", "").strip()

    try:
        tz_obj = pytz_timezone(tz_name)
        from_date = parse_date(from_str)
        to_date = parse_date(to_str)
        from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
        to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
    except Exception as e:
        return Response({"status": 0, "message": f"Invalid date: {e}"}, status=400)

    # ✅ Clicks
    clicks_qs = Click.objects.filter(
        affiliate=user, created_at__range=(from_dt, to_dt)
    )
    if country:
        clicks_qs = clicks_qs.filter(country__iexact=country)

    clicks_data = clicks_qs.values("device").annotate(
        hosts=Count("ip", distinct=True),
        clicks=Count("id")
    )

    # ✅ Conversions
    conv_qs = Conversion.objects.filter(
        affiliate=user, created_at__range=(from_dt, to_dt), status="approved"
    )
    if country:
        conv_qs = conv_qs.filter(country__iexact=country)

    conv_data = conv_qs.values("device").annotate(
        approved=Count("id"),
        total=Sum("payout")
    )

    click_map = {c["device"]: c for c in clicks_data}
    conv_map = {c["device"]: c for c in conv_data}

    devices = set(click_map.keys()) | set(conv_map.keys())

    results = []
    for device in devices:
        click = click_map.get(device, {})
        conv = conv_map.get(device, {})
        results.append({
            "device": device or "Unknown",
            "hosts": click.get("hosts", 0),
            "clicks": click.get("clicks", 0),
            "approved": conv.get("approved", 0),
            "total": float(conv.get("total") or 0),
        })

    return Response({"status": 1, "results": results})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def country_breakdown(request):
    user = request.user
    from_str = request.GET.get("from")
    to_str = request.GET.get("to")
    tz_name = request.GET.get("timezone", "America/New_York")

    try:
        tz_obj = pytz_timezone(tz_name)
        from_date = parse_date(from_str)
        to_date = parse_date(to_str)
        from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
        to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
    except Exception as e:
        return Response({"status": 0, "message": str(e)}, status=400)

    # ✅ Clicks per country
    clicks_qs = Click.objects.filter(
        affiliate=user, created_at__range=(from_dt, to_dt)
    ).values("country").annotate(
        hosts=Count("ip", distinct=True),
        clicks=Count("id")
    )

    # ✅ Approved conversions
    convs_qs = Conversion.objects.filter(
        affiliate=user, created_at__range=(from_dt, to_dt), status="approved"
    ).values("country").annotate(
        approved=Count("id"),
        total=Sum("payout")
    )

    click_map = {i["country"]: i for i in clicks_qs}
    conv_map = {i["country"]: i for i in convs_qs}

    all_countries = set(click_map.keys()) | set(conv_map.keys())

    results = []
    for c in all_countries:
        clicks = click_map.get(c, {})
        convs = conv_map.get(c, {})
        results.append({
            "country": c or "Unknown",
            "hosts": clicks.get("hosts", 0),
            "clicks": clicks.get("clicks", 0),
            "approved": convs.get("approved", 0),
            "total": float(convs.get("total") or 0),
        })

    return Response({"status": 1, "results": results})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def city_breakdown(request):
    user = request.user
    from_str = request.GET.get("from")
    to_str = request.GET.get("to")
    tz_name = request.GET.get("timezone", "America/New_York")

    try:
        tz_obj = pytz_timezone(tz_name)
        from_date = parse_date(from_str)
        to_date = parse_date(to_str)
        from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
        to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
    except Exception as e:
        return Response({"status": 0, "message": str(e)}, status=400)

    # ✅ Clicks per city
    clicks_qs = Click.objects.filter(
        affiliate=user,
        created_at__range=(from_dt, to_dt)
    ).values("city").annotate(
        hosts=Count("ip", distinct=True),
        clicks=Count("id")
    )

    # ✅ Approved conversions per city
    convs_qs = Conversion.objects.filter(
        affiliate=user,
        created_at__range=(from_dt, to_dt),
        status="approved"
    ).values("city").annotate(
        approved=Count("id"),
        total=Sum("payout")
    )

    click_map = {i["city"]: i for i in clicks_qs}
    conv_map = {i["city"]: i for i in convs_qs}
    all_cities = set(click_map.keys()) | set(conv_map.keys())

    results = []
    for city in all_cities:
        clicks = click_map.get(city, {})
        conv = conv_map.get(city, {})
        results.append({
            "city": city or "Unknown",
            "hosts": clicks.get("hosts", 0),
            "clicks": clicks.get("clicks", 0),
            "approved": conv.get("approved", 0),
            "total": float(conv.get("total") or 0),
        })

    return Response({"status": 1, "results": results})


from django.db.models import Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.dateparse import parse_date
from datetime import datetime
from pytz import timezone as pytz_timezone
from tracker.models import Click, Conversion, APPROVED_STATUS


class Sub1HostStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from_str = request.GET.get("from")
        to_str = request.GET.get("to")
        tz_name = request.GET.get("timezone", "UTC")

        try:
            tz_obj = pytz_timezone(tz_name)
            from_date = parse_date(from_str)
            to_date = parse_date(to_str)
            from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
            to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
        except Exception as e:
            return Response({"status": 0, "message": f"Invalid date: {e}"}, status=400)

        # ✅ Clicks per Sub1
        click_qs = Click.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt)
        ).values("sub1").annotate(
            hosts=Count("ip", distinct=True),
            clicks=Count("id")
        )

        # ✅ Approved Conversions per Sub1
        conv_qs = Conversion.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt),
            status=APPROVED_STATUS
        ).values("sub1").annotate(
            approved=Count("id"),
            total=Count("payout")  # or Sum if payout values matter
        )

        conv_map = {item["sub1"] or "Undefined": item for item in conv_qs}

        # ✅ Merge both
        results = []
        for row in click_qs:
            sub1 = row["sub1"] or "Undefined"
            conv = conv_map.get(sub1, {})
            results.append({
                "sub1": sub1,
                "hosts": row["hosts"],
                "clicks": row["clicks"],
                "approved": conv.get("approved", 0),
                "total": float(conv.get("total") or 0.0),
            })

        return Response({"status": 1, "results": results})

class Sub2HostStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from_str = request.GET.get("from")
        to_str = request.GET.get("to")
        tz_name = request.GET.get("timezone", "UTC")

        try:
            tz_obj = pytz_timezone(tz_name)
            from_date = parse_date(from_str)
            to_date = parse_date(to_str)
            from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
            to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
        except Exception as e:
            return Response({"status": 0, "message": f"Invalid date: {e}"}, status=400)

        # ✅ Clicks per sub2
        click_qs = Click.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt)
        ).values("sub2").annotate(
            hosts=Count("ip", distinct=True),
            clicks=Count("id")
        )

        # ✅ Approved conversions per sub2
        conv_qs = Conversion.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt),
            status=APPROVED_STATUS
        ).values("sub2").annotate(
            approved=Count("id"),
            total=Sum("payout")
        )

        conv_map = {item["sub2"] or "Undefined": item for item in conv_qs}

        # ✅ Merge both
        results = []
        for row in click_qs:
            sub2 = row["sub2"] or "Undefined"
            conv = conv_map.get(sub2, {})
            results.append({
                "sub2": sub2,
                "hosts": row["hosts"],
                "clicks": row["clicks"],
                "approved": conv.get("approved", 0),
                "total": float(conv.get("total") or 0.0),
            })

        return Response({"status": 1, "results": results})


class Sub3HostStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from_str = request.GET.get("from")
        to_str = request.GET.get("to")
        tz_name = request.GET.get("timezone", "UTC")

        try:
            tz_obj = pytz_timezone(tz_name)
            from_date = parse_date(from_str)
            to_date = parse_date(to_str)
            from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
            to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
        except Exception as e:
            return Response({"status": 0, "message": f"Invalid date: {e}"}, status=400)

        # ✅ Clicks per sub3
        click_qs = Click.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt)
        ).values("sub3").annotate(
            hosts=Count("ip", distinct=True),
            clicks=Count("id")
        )

        # ✅ Approved conversions per sub3
        conv_qs = Conversion.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt),
            status=APPROVED_STATUS
        ).values("sub3").annotate(
            approved=Count("id"),
            total=Sum("payout")
        )

        conv_map = {item["sub3"] or "Undefined": item for item in conv_qs}

        # ✅ Merge both
        results = []
        for row in click_qs:
            sub3 = row["sub3"] or "Undefined"
            conv = conv_map.get(sub3, {})
            results.append({
                "sub3": sub3,
                "hosts": row["hosts"],
                "clicks": row["clicks"],
                "approved": conv.get("approved", 0),
                "total": float(conv.get("total") or 0.0),
            })

        return Response({"status": 1, "results": results})

class Sub4HostStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from_str = request.GET.get("from")
        to_str = request.GET.get("to")
        tz_name = request.GET.get("timezone", "UTC")

        try:
            tz_obj = pytz_timezone(tz_name)
            from_date = parse_date(from_str)
            to_date = parse_date(to_str)
            from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
            to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
        except Exception as e:
            return Response({"status": 0, "message": f"Invalid date: {e}"}, status=400)

        # ✅ Clicks per sub4
        click_qs = Click.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt)
        ).values("sub4").annotate(
            hosts=Count("ip", distinct=True),
            clicks=Count("id")
        )

        # ✅ Approved conversions per sub4
        conv_qs = Conversion.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt),
            status=APPROVED_STATUS
        ).values("sub4").annotate(
            approved=Count("id"),
            total=Sum("payout")
        )

        conv_map = {item["sub4"] or "Undefined": item for item in conv_qs}

        results = []
        for row in click_qs:
            sub4 = row["sub4"] or "Undefined"
            conv = conv_map.get(sub4, {})
            results.append({
                "sub4": sub4,
                "hosts": row["hosts"],
                "clicks": row["clicks"],
                "approved": conv.get("approved", 0),
                "total": float(conv.get("total") or 0.0),
            })

        return Response({"status": 1, "results": results})

class Sub5HostStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from_str = request.GET.get("from")
        to_str = request.GET.get("to")
        tz_name = request.GET.get("timezone", "UTC")

        try:
            tz_obj = pytz_timezone(tz_name)
            from_date = parse_date(from_str)
            to_date = parse_date(to_str)
            from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
            to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
        except Exception as e:
            return Response({"status": 0, "message": f"Invalid date: {e}"}, status=400)

        # ✅ Clicks per sub5
        click_qs = Click.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt)
        ).values("sub5").annotate(
            hosts=Count("ip", distinct=True),
            clicks=Count("id")
        )

        # ✅ Approved conversions per sub5
        conv_qs = Conversion.objects.filter(
            affiliate=user,
            created_at__range=(from_dt, to_dt),
            status=APPROVED_STATUS
        ).values("sub5").annotate(
            approved=Count("id"),
            total=Sum("payout")
        )

        conv_map = {item["sub5"] or "Undefined": item for item in conv_qs}

        results = []
        for row in click_qs:
            sub5 = row["sub5"] or "Undefined"
            conv = conv_map.get(sub5, {})
            results.append({
                "sub5": sub5,
                "hosts": row["hosts"],
                "clicks": row["clicks"],
                "approved": conv.get("approved", 0),
                "total": float(conv.get("total") or 0.0),
            })

        return Response({"status": 1, "results": results})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def isp_breakdown(request):
    user = request.user
    from_str = request.GET.get("from")
    to_str = request.GET.get("to")
    tz_name = request.GET.get("timezone", "UTC")

    try:
        tz_obj = pytz_timezone(tz_name)
        from_date = parse_date(from_str)
        to_date = parse_date(to_str)
        from_dt = tz_obj.localize(datetime.combine(from_date, datetime.min.time()))
        to_dt = tz_obj.localize(datetime.combine(to_date, datetime.max.time()))
    except Exception as e:
        return Response({"status": 0, "message": f"Invalid date: {e}"}, status=400)

    # ✅ Clicks per ISP
    click_qs = Click.objects.filter(
        affiliate=user,
        created_at__range=(from_dt, to_dt)
    ).values("isp").annotate(
        hosts=Count("ip", distinct=True),
        clicks=Count("id")
    )

    # ✅ Approved Conversions per ISP
    conv_qs = Conversion.objects.filter(
        affiliate=user,
        created_at__range=(from_dt, to_dt),
        status="approved"
    ).values("isp").annotate(
        approved=Count("id"),
        total=Sum("payout")
    )

    conv_map = {item["isp"] or "Unknown": item for item in conv_qs}

    # ✅ Merge
    results = []
    for row in click_qs:
        isp = row["isp"] or "Unknown"
        conv = conv_map.get(isp, {})
        results.append({
            "isp": isp,
            "hosts": row["hosts"],
            "clicks": row["clicks"],
            "approved": conv.get("approved", 0),
            "total": float(conv.get("total") or 0.0),
        })

    return Response({"status": 1, "results": results})
