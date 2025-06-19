from django.urls import path
from tracker.statistics.views import browser_breakdown
from tracker.statistics.views import device_breakdown
from tracker.statistics.views import os_breakdown
from tracker.statistics.views import Sub1HostStatsAPIView
from tracker.statistics.views import Sub2HostStatsAPIView
from tracker.statistics.views import Sub3HostStatsAPIView
from tracker.statistics.views import Sub4HostStatsAPIView
from tracker.statistics.views import Sub5HostStatsAPIView
from .views import isp_breakdown
from tracker.statistics.views import country_breakdown
from tracker.statistics.views import city_breakdown
from tracker.statistics.views import (
    DailyStatAPIView,
    conversion_report_latest,
    AffiliateOfferBreakdownAPIView,
)

urlpatterns = [
    path('daily/', DailyStatAPIView.as_view(), name='statistics-daily'),
    path('conversions/latest/', conversion_report_latest, name='statistics-conversions-latest'),
    path('offers-breakdown/', AffiliateOfferBreakdownAPIView.as_view(), name='statistics-offers-breakdown'),
    path("browsers/", browser_breakdown, name="statistics-browsers"),
    path("os-breakdown/", os_breakdown, name="statistics-os-breakdown"),
    path("devices/", device_breakdown, name="statistics-devices"),
    path("countries/", country_breakdown, name="statistics-countries"),
    path("cities/", city_breakdown, name="statistics-cities"),
    path('sub1-host/', Sub1HostStatsAPIView.as_view(), name='sub1-host-stats'),
    path('sub2-host/', Sub2HostStatsAPIView.as_view(), name='sub2-host-stats'),
    path('sub3-host/', Sub2HostStatsAPIView.as_view(), name='sub3-host-stats'),
    path('sub4-host/', Sub2HostStatsAPIView.as_view(), name='sub3-host-stats'),
    path('sub5-host/', Sub2HostStatsAPIView.as_view(), name='sub3-host-stats'),
    path('mobile-isp/', isp_breakdown, name="mobile-isp"),


]

