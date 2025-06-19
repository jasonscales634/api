from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

User = get_user_model()

class AffiliateModelSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='first_name')

    class Meta:
        model = User
        fields = (
            'name',
            'email',  # যদি চাই email ও পাঠাতে
        )


class AffiliateRetrieveAPIView(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AffiliateModelSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
