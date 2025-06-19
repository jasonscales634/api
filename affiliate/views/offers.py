import django_filters
from rest_framework import generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from countries_plus.models import Country
from django.conf import settings
from offer.models import (
    Offer,
    Category,
    Currency,
    Goal,
    TrafficSource,
    OfferTrafficSource,
    Payout
)
from ..filters import CommaSeparatedTextFilter


# ---------- Serializers ----------

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('iso',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)


class TrafficSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficSource
        fields = ('name',)


class OfferTrafficSourceSerializer(serializers.ModelSerializer):
    name = serializers.SlugRelatedField(
        source='traffic_source',
        many=False, read_only=True, slug_field='name'
    )

    class Meta:
        model = OfferTrafficSource
        fields = ('name', 'allowed')


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ('name',)


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('code', 'name')


class PayoutSerializer(serializers.ModelSerializer):
    countries = CountrySerializer(many=True, read_only=True)
    goal = GoalSerializer(read_only=True)
    currency = CurrencySerializer(read_only=True)

    class Meta:
        model = Payout
        fields = ('payout', 'countries', 'type', 'currency', 'goal')


class OfferSerializer(serializers.ModelSerializer):
    countries = CountrySerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    traffic_sources = OfferTrafficSourceSerializer(
        source='offertrafficsource_set', many=True, read_only=True)
    payouts = PayoutSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = (
            'id',
            'title',
            'description',
            'description_html',
            'preview_link',
            'icon',
            'countries',
            'categories',
            'traffic_sources',
            'payouts',
        )


# ---------- Filters ----------

class OfferFilterSet(django_filters.FilterSet):
    categories = CommaSeparatedTextFilter(
        field_name='categories',
        help_text='Exact category name or comma-separated names list'
    )
    countries = CommaSeparatedTextFilter(
        field_name='countries',
        help_text='Country 2-character code or comma-separated list'
    )


# ---------- Views ----------

class OfferListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = OfferFilterSet
    search_fields = ['=id', 'title']
    ordering_fields = ['id', 'title']


class OfferRetrieveView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OfferSerializer
    queryset = Offer.objects.all()


def generate_tracking_link(offer_id: int, pid: int) -> str:
    base_url = settings.TRACKER_URL
    return f"{base_url}/click?offer_id={offer_id}&pid={pid}"


class TrackingLinkView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        offer_id = pk
        user_id = request.user.id

        # সহজ সংস্করণ: সবাই ট্র্যাকিং লিংক পায়
        url = generate_tracking_link(offer_id, user_id)
        return Response({'url': url})

        # উন্নত সংস্করণ (access check সহ)
        # from offer.constants import ACCESS_TYPE_PUBLIC, ACCESS_TYPE_PREMODERATION, APPROVAL_STATUS_APPROVED
        # from offer.models import Approval
        #
        # offer = get_object_or_404(Offer, pk=offer_id)
        #
        # if offer.access == ACCESS_TYPE_PUBLIC:
        #     return Response({'url': generate_tracking_link(offer_id, user_id)})
        #
        # elif offer.access == ACCESS_TYPE_PREMODERATION:
        #     approved = Approval.objects.filter(
        #         offer_id=offer_id,
        #         affiliate_id=user_id,
        #         status=APPROVAL_STATUS_APPROVED
        #     ).exists()
        #     if approved:
        #         return Response({'url': generate_tracking_link(offer_id, user_id)})
        #     else:
        #         return Response(status=403)
        #
        # else:
        #     return Response(status=403)