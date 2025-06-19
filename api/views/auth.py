# api/views/auth.py

from rest_framework_simplejwt.views import TokenObtainPairView
from api.serializers import CustomTokenObtainPairSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers

class EmailTokenSchema(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(request_body=EmailTokenSchema)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
