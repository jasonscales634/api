#C:\Users\MD BASARULL ISLAM\Downloads\adcpaapi1-main (1)\adcpaapi1-main\affiliate\urls.py

from django.urls import path
from .views.views import WalletView
from .views import AffiliateDashboardAPIView
from affiliate.views.stats import OverviewStatsView
from .views.register import register_page
from .views.profile import AffiliateRetrieveAPIView
from .views.offers import OfferListView, OfferRetrieveView, TrackingLinkView
from .views.manager import ManagerInfoAPIView
from .views.stats import (
    DailyStatsView,
    OffersStatsView,
    GoalStatsView,
    SubStatsView,
)
from .views.conversions import ConversionListView

urlpatterns = [
    # ✅ Dashboard Manager Info API
    path('dashboard/info/', AffiliateDashboardAPIView.as_view(), name='dashboard-info'),

    # ✅ Affiliate Registration Form (HTML)
    path("register-form/", register_page, name="affiliate-register-form"),

    # ✅ Affiliate Profile API
    path('profile/', AffiliateRetrieveAPIView.as_view(), name='affiliate-profile'),

    # ✅ Offers Endpoints
    path('offers/', OfferListView.as_view(), name='affiliate-offers'),
    path('offers/<int:pk>/', OfferRetrieveView.as_view(), name='affiliate-offer'),
    path('offers/<int:pk>/tracking-link/', TrackingLinkView.as_view(), name='affiliate-offer-tracking-link'),

    # ✅ Stats Endpoints
    path('stats/daily/', DailyStatsView.as_view(), name='affiliate-stats-daily'),
    path('stats/offers/', OffersStatsView.as_view(), name='affiliate-stats-offers'),
    path('stats/by-goal/', GoalStatsView.as_view(), name='affiliate-stats-by-goal'),
    path('stats/by-sub/<str:sub>/', SubStatsView.as_view(), name='affiliate-stats-by-sub'),

    # ✅ Conversions Endpoint
    path('conversions/', ConversionListView.as_view(), name='affiliate-conversions'),
    path("manager-profile/", ManagerInfoAPIView.as_view()),
    path('stats/overview/', OverviewStatsView.as_view(), name='affiliate-stats-overview'),
    path('wallet/', WalletView.as_view(), name='wallet'),


]



