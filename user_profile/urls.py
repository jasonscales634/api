from django.urls import path
from .views import UserProfileDetailsView
from .views import (
    EmailLoginView,
    UserProfileView,
    RequestPasswordResetAPIView,
    VerifyResetTokenHTMLView,
    ResetPasswordAPIView,
)
from .views import VerifyEmailAPIView

urlpatterns = [
    # 🔐 Email-based JWT Login
    path('login/', EmailLoginView.as_view(), name='email_login'),

    # 👤 User Profile Info
    path('me/', UserProfileView.as_view(), name='user_profile'),

    # 🔒 Password Reset Flow
    path('request-reset/', RequestPasswordResetAPIView.as_view(), name='request_reset'),
    path('verify-reset/', VerifyResetTokenHTMLView.as_view(), name='verify_reset'),
    path('reset-password/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify_email'),
    path('me/profile/', UserProfileDetailsView.as_view(), name='user-profile-details'),
]




