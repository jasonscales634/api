from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Sum
from analytics.statistics.models.statistics import DailyStat
from analytics.statistics.serializers.breakdowns import (
    CombinedBreakdownSerializer,
    DeviceBreakdownSerializer,
    OSBreakdownSerializer
)


class CombinedBreakdownAPIView(APIView):
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        affiliate_id = request.GET.get('affiliate')

        qs = DailyStat.objects.all()

        if start_date and end_date:
            qs = qs.filter(date__range=[start_date, end_date])

        if affiliate_id:
            qs = qs.filter(affiliate_id=affiliate_id)

        data = qs.values('country', 'device', 'os').annotate(
            raw_clicks=Sum('raw_clicks'),
            unique_clicks=Sum('unique_clicks'),
            conversions=Sum('conversions'),
            revenue=Sum('revenue'),
            earning=Sum('earning')
        ).order_by('-revenue')

        serializer = CombinedBreakdownSerializer(data=list(data), many=True)
        serializer.is_valid()  # No DB validation needed; ensures output shape
        return Response({
            "status": 1,
            "results": serializer.data
        })


@api_view(['GET'])
def device_breakdown(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    qs = DailyStat.objects.all()
    if start_date and end_date:
        qs = qs.filter(date__range=[start_date, end_date])

    data = qs.values('device').annotate(
        clicks=Sum('raw_clicks'),
        conversions=Sum('conversions')
    )

    serializer = DeviceBreakdownSerializer(data=list(data), many=True)
    serializer.is_valid()
    return Response({
        "status": 1,
        "results": serializer.data
    })


@api_view(['GET'])
def os_breakdown(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    qs = DailyStat.objects.all()
    if start_date and end_date:
        qs = qs.filter(date__range=[start_date, end_date])

    data = qs.values('os').annotate(
        clicks=Sum('raw_clicks'),
        conversions=Sum('conversions')
    )

    serializer = OSBreakdownSerializer(data=list(data), many=True)
    serializer.is_valid()
    return Response({
        "status": 1,
        "results": serializer.data
    })
