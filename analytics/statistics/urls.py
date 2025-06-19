from django.urls import path

# ✅ Affiliate stats views
from analytics.statistics.views.by_affiliate import AffiliateStatsAPIView, DailyAffiliateStatsView

# ✅ Other views
from analytics.statistics.views.custom_statistics import CustomStatisticsAPIView
from analytics.statistics.views.by_country import CountryListAPIView, CountryBreakdownAPIView
from analytics.statistics.views.clicks import ClickListAPIView
from analytics.statistics.views.export_csv import export_combined_csv
from analytics.statistics.views.summary import statistics_summary

from analytics.statistics.views.by_offer import OfferBreakdownAPIView
from analytics.statistics.views.by_goal import GoalBreakdownAPIView
from analytics.statistics.views.top_offers import TopOffersAPIView
from analytics.statistics.views.combined_breakdown import (
    CombinedBreakdownAPIView,
    device_breakdown,
    os_breakdown,
)

urlpatterns = [
    # 📊 Affiliate stats
    path('affiliate/', AffiliateStatsAPIView.as_view(), name='affiliate-stats'),
    path('affiliate/stats/daily/', DailyAffiliateStatsView.as_view(), name='daily-stats'),

    # 🔍 Custom filters and summaries
    path('custom/', CustomStatisticsAPIView.as_view(), name='custom-statistics'),
    path('summary/', statistics_summary, name='statistics-summary'),

    # 🌍 Country breakdown
    path('countries/list/', CountryListAPIView.as_view(), name='country-list'),
    path('countries/breakdown/', CountryBreakdownAPIView.as_view(), name='country-breakdown'),

    # 🖱 Clicks & conversions
    path('clicks/', ClickListAPIView.as_view(), name='clicks-list'),


    # 📈 Offer/Goal-based breakdowns
    path('offers-breakdown/', OfferBreakdownAPIView.as_view(), name='offers-breakdown'),
    path('statistics/by-offer/', OfferBreakdownAPIView.as_view(), name='by-offer'),
    path('statistics/by-goal/', GoalBreakdownAPIView.as_view(), name='by-goal'),

    # 🧠 Combined breakdowns
    path('combined-breakdown/', CombinedBreakdownAPIView.as_view(), name='combined-breakdown'),
    path('combined-breakdown/export-csv/', export_combined_csv, name='export-csv'),
    path('statistics/by-device/', device_breakdown, name='statistics-device'),
    path('statistics/by-os/', os_breakdown, name='statistics-os'),

    # 🏆 Top offers
    path('top-offers/', TopOffersAPIView.as_view(), name='top-offers'),
]