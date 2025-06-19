from django.urls import path, include

from analytics.statistics.views.by_country import CountryListAPIView
from analytics.statistics.views.custom_statistics import CustomStatisticsAPIView
from analytics.statistics.views.by_affiliate import AffiliateStatsAPIView



urlpatterns = [
    path('countries/', CountryListAPIView.as_view(), name='country-list'),
    path('custom/', CustomStatisticsAPIView.as_view(), name='custom-statistics'),
    path('affiliate/', AffiliateStatsAPIView.as_view(), name='stats-by-affiliate'),
    path('statistics/', include('analytics.statistics.urls')),

    path("statistics/daily-chart/", CustomStatisticsAPIView.as_view(), name='statistics_last_30_days'),
    path("statistics/top-offers/", CustomStatisticsAPIView.as_view(), name='top_offers_chart'),
    path("statistics/goal-breakdown/", CustomStatisticsAPIView.as_view(), name='goal_breakdown_chart'),
    path('statistics/custom/', CustomStatisticsAPIView.as_view(), name='custom-statistics'),


]