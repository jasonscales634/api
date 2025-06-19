from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from analytics.statistics.models.statistics import DailyStat
from offer.models import Goal  # ✅ ঠিক path
from analytics.statistics.serializers.by_goal import GoalBreakdownSerializer


class GoalBreakdownAPIView(APIView):
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        stats = DailyStat.objects.all()
        if start_date and end_date:
            stats = stats.filter(date__range=[start_date, end_date])

        data = stats.values('goal_id').annotate(
            raw_clicks=Sum('raw_clicks'),
            unique_clicks=Sum('unique_clicks'),
            conversions=Sum('conversions'),
            revenue=Sum('revenue'),
            earning=Sum('earning'),
        ).order_by('-revenue')

        # ✅ Goal-এর নাম map করা
        goal_map = {goal.id: goal for goal in Goal.objects.filter(id__in=[d['goal_id'] for d in data])}
        for d in data:
            goal = goal_map.get(d['goal_id'])
            d['goal_title'] = goal.name if goal else ""
            d['goal_id'] = str(goal.id) if goal else ""

        serializer = GoalBreakdownSerializer(data, many=True)
        return Response({
            "status": 1,
            "results": serializer.data
        })