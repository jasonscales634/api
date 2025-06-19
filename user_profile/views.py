# user_profile/views.py

from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import ProfileSerializer
from .serializers import UserSerializer, EmailLoginSerializer
from .utils import send_password_reset_email

User = get_user_model()


# 🔐 JWT Login (Email)
class EmailLoginView(TokenObtainPairView):
    serializer_class = EmailLoginSerializer


# 👤 Get Profile
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)


# 🔒 Step 1: Request password reset
class RequestPasswordResetAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Email is required.'}, status=400)
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user)
            return Response({'detail': 'Reset link sent to your email.'})
        except User.DoesNotExist:
            return Response({'detail': 'No account with that email.'}, status=404)


# 🔒 Step 2: Show HTML reset form (using token)
class VerifyResetTokenHTMLView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'detail': 'Token is required'}, status=400)
        try:
            user = User.objects.get(reset_token=token)
            if user.reset_token_expiry < timezone.now():
                return Response({'detail': 'Token expired'}, status=400)
            return render(request._request, 'reset_form.html', {'token': token})
        except User.DoesNotExist:
            return Response({'detail': 'Invalid token'}, status=404)


# 🔒 Step 3: Reset password using token
class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('password')

        if not token or not new_password:
            return Response({'detail': 'Token and password are required.'}, status=400)

        try:
            user = User.objects.get(reset_token=token)
            if user.reset_token_expiry < timezone.now():
                return Response({'detail': 'Token expired'}, status=400)

            user.set_password(new_password)
            user.reset_token = None
            user.reset_token_expiry = None
            user.save()

            return Response({'detail': 'Password reset successful'})
        except User.DoesNotExist:
            return Response({'detail': 'Invalid token'}, status=404)


# ✅ Verify email via token
class VerifyEmailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get('token')
        if not token:
            return Response({'detail': 'Token is required'}, status=400)
        try:
            user = User.objects.get(verification_token=token)
            if user.token_expiry < timezone.now():
                return Response({'detail': 'Token expired'}, status=400)

            user.is_verified = True
            user.verification_token = None
            user.token_expiry = None
            user.save()

            return Response({'detail': '✅ Email verified successfully'})
        except User.DoesNotExist:
            return Response({'detail': 'Invalid token'}, status=404)




class UserProfileDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'main_profile', None)
        if not profile:
            return Response({'detail': 'Profile not found.'}, status=404)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

