from django.urls import path
from .views import AffiliateDashboardAPIView

urlpatterns = [
    path('dashboard/info/', AffiliateDashboardAPIView.as_view(), name='affiliate-dashboard-info'),
]
