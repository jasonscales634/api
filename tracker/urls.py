from django.urls import path
from django.urls import path, include
from tracker.views import AffiliateLiveStatsAPIView
from tracker.views import DashboardSummaryAPIView
from tracker.views import (
    postback,
    track_click,
    debug_click_view,
    legacy_click_redirect,
    MyClickListAPIView
)
from tracker.api_views import ClickListAPIView, ConversionListAPIView

urlpatterns = [
    path('postback/', postback, name='tracker-postback'),
    path('clicks/', ClickListAPIView.as_view(), name='clicks-list'),
    path('conversions/', ConversionListAPIView.as_view(), name='conversions-list'),
    path('track/', track_click, name='track-click'),
    path('debug-click/', debug_click_view, name='tracker-debug'),
    path('click/', legacy_click_redirect, name='legacy-click-redirect'),
    path('my-clicks/', MyClickListAPIView.as_view(), name='my-clicks'),
    path('api/dashboard-summary/', DashboardSummaryAPIView.as_view(), name='dashboard-summary'),
    path('api/affiliate/stats/live/', AffiliateLiveStatsAPIView.as_view()),
    path('api/statistics/', include('tracker.statistics.urls')),
]

