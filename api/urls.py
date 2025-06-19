from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views.auth import CustomTokenObtainPairView
from .views.affiliate import affiliate_register
from .views.conversions import (
    ConversionCreateView,
    AdminConversionListView,
)
from .views.offer import OfferViewSet
from .views.advertiser import AdvertiserViewSet
from .views.landing import LandingViewSet
from .views.payout import PayoutViewSet
from .views.offer_traffic_source import OfferTrafficSourceViewSet

router = DefaultRouter()
router.register(r'offers', OfferViewSet)
router.register(r'advertisers', AdvertiserViewSet)
router.register(r'landings', LandingViewSet)
router.register(r'payouts', PayoutViewSet)
router.register(r'traffic-sources', OfferTrafficSourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('affiliate/register/', affiliate_register, name='affiliate-register'),
    path('conversions/', ConversionCreateView.as_view(), name='conversion-create'),
    path('admin/conversions/', AdminConversionListView.as_view(), name='admin-conversion-list'),
]
