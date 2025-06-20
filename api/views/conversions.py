#D:\project\api\views\conversions.py

from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from webargs import core, fields, ValidationError
from webargs.djangoparser import parser
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from tracker.models import Conversion, conversion_statuses, REJECTED_STATUS
from user_profile.permissions import IsSuperUser
from offer.models import Currency, Goal


# Serializers
class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('code', 'name')


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ('id', 'name')


class ConversionSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(allow_null=True)
    goal = GoalSerializer()

    class Meta:
        model = Conversion
        fields = (
            'id',
            'created_at',
            'offer_id',
            'affiliate_id',
            'revenue',
            'payout',
            'currency',
            'sub1', 'sub2', 'sub3', 'sub4', 'sub5',
            'status',
            'goal',
            'goal_value',
            'country',
            'ip',
            'ua',
        )


# Validation functions
@parser.location_loader('data')
def parse_data(request, name, field):
    return core.get_value(request.data, name, field)


def user_must_exist_in_db(user_id: int) -> None:
    try:
        get_user_model().objects.get(pk=user_id)
    except get_user_model().DoesNotExist:
        raise ValidationError("Affiliate does not exist")


def status_must_be_known(status: str) -> None:
    if status and status not in map(lambda r: r[0], conversion_statuses):
        raise ValidationError("Wrong status value")


# POST argument definitions
conversion_create_args = {
    'offer_id': fields.Int(required=True),
    'pid': fields.Int(required=True, validate=user_must_exist_in_db),
    'status': fields.Str(load_default=REJECTED_STATUS, validate=status_must_be_known),
    'currency': fields.Str(load_default=''),
    'goal': fields.Str(load_default=''),
    'revenue': fields.Float(load_default=0.0),
    'payout': fields.Float(load_default=0.0),
    'sub1': fields.Str(load_default=''),
    'goal_id': fields.Int(load_default=None),
}


# POST: Create a new conversion (admin only)
class ConversionCreateView(APIView):
    permission_classes = (IsAuthenticated, IsSuperUser,)
    serializer_class = ConversionSerializer

    @parser.use_args(conversion_create_args)
    def post(self, request, args):
        usr = get_user_model().objects.get(pk=args['pid'])

        conversion = Conversion(
            offer_id=args['offer_id'],
            affiliate_id=args['pid'],
            affiliate_manager=usr.profile.manager,
            goal_value=args['goal'],
            revenue=args['revenue'],
            payout=args['payout'],
            sub1=args['sub1'],
            currency=Currency.objects.filter(code=args['currency']).first(),
            status=args['status']
        )

        if args['goal_id']:
            conversion.goal_id = args['goal_id']

        conversion.save()
        return Response(ConversionSerializer(conversion).data, status=status.HTTP_201_CREATED)


# GET: Admin-only conversion list with summary
class AdminConversionListView(APIView):
    permission_classes = (IsAuthenticated, IsSuperUser,)
    serializer_class = ConversionSerializer

    def get(self, request):
        conversions = Conversion.objects.all().select_related('currency', 'goal')
        serialized = ConversionSerializer(conversions, many=True)

        summary = conversions.aggregate(
            total_revenue=Sum('revenue'),
            total_payout=Sum('payout'),
            total_count=Count('id')
        )

        return Response({
            'conversions': serialized.data,
            'summary': summary
        })
