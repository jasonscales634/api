from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from analytics.admin_dashboard import custom_admin_site
from project.views import redirect_view, home_view

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', custom_admin_site.urls),

    # Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Modules
    path('api/user/', include('user_profile.urls')),
    path('api/affiliate/', include('affiliate.urls')),
    path('api/network/', include('network.urls')),
    path('api/payments/', include('payments.urls')),
    path('userbilling/', include('payments.userbilling.urls')),
    path('api/offer/', include('offer.urls')),
    path('api/dictionaries/', include('dictionaries.urls')),
    path('api/', include('api.urls')),

    # Analytics (Main and Statistics)
    path('api/analytics/', include('analytics.urls')),
    path('api/statistics/', include('analytics.statistics.urls')),

    # Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='redoc'),

    # Misc
    path('redirect/', redirect_view, name='custom-redirect'),
    path('', home_view, name='home'),
    path('', include('tracker.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
