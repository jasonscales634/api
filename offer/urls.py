from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, LandingListCreateView, LandingDetailView, clone_offer_view
from . import views

router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offers')

urlpatterns = [
    path('', include(router.urls)),

    # Landings
    path('offers/<int:offer_id>/landings/', LandingListCreateView.as_view(), name='landing-list'),
    path('offers/<int:offer_id>/landings/<int:pk>/', LandingDetailView.as_view(), name='landing-detail'),

    # Top Offers
    path('top/', views.top_offers, name='top-offers'),

    # Clone offer (Admin only)
    path('admin/offer/clone/<int:pk>/', clone_offer_view, name='clone_offer'),
]
