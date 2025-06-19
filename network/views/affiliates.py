from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model

# ✅ Ensure this path is correct (adjust based on your project structure)
from user_profile.permissions import IsAdminOrSuperUser

User = get_user_model()

# ✅ Serializer
class AffiliateSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'full_name',
        )

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

# ✅ List all affiliates
class AffiliateListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = AffiliateSerializer

    def get_queryset(self):
        return User.objects.filter(
            is_staff=False,
            profile__manager__isnull=False
        )

# ✅ Retrieve a specific affiliate
class AffiliateRetrieveView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperUser]
    serializer_class = AffiliateSerializer

    def get_queryset(self):
        return User.objects.filter(
            is_staff=False,
            profile__manager__isnull=False
        )
