from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from django.http import HttpResponse
from reportlab.pdfgen import canvas

from .models import Payment, StatusLog, PaymentStatusLog
from .serializers import PaymentSerializer, PaymentDetailSerializer
from payments.userbilling.models import UserBillingInfo
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_request(request):
    data = request.data.copy()
    data['user'] = request.user.id
    method = data.get("method")

    if method == "bank":
        if not data.get("account_number") or not data.get("bank_name"):
            return Response({"error": "Bank details required."}, status=400)
    elif method == "paypal":
        if not data.get("payment_email"):
            return Response({"error": "PayPal email required."}, status=400)
    elif method == "crypto":
        if not data.get("wallet_address") or not data.get("crypto_network"):
            return Response({"error": "Crypto wallet address & network required."}, status=400)

    serializer = PaymentSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response({'message': 'Withdrawal request submitted', 'data': serializer.data}, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_payments(request):
    payments = Payment.objects.filter(user=request.user, is_deleted=False).order_by('-created_at')
    paginator = PageNumberPagination()
    paginated = paginator.paginate_queryset(payments, request)
    serializer = PaymentSerializer(paginated, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_payments(request):
    payments = Payment.objects.filter(is_deleted=False).order_by('-created_at')
    paginator = PageNumberPagination()
    paginated = paginator.paginate_queryset(payments, request)
    serializer = PaymentSerializer(paginated, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_payment_status(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

    status_value = request.data.get("status")
    if status_value not in ['approved', 'rejected', 'completed']:
        return Response({"error": "Invalid status"}, status=400)

    old_status = payment.status
    payment.status = status_value
    payment.save()

    PaymentStatusLog.objects.create(
        payment=payment,
        old_status=old_status,
        new_status=status_value,
        changed_by=request.user
    )
    StatusLog.objects.create(
        payment=payment,
        previous_status=old_status,
        new_status=status_value,
        updated_by=request.user
    )

    send_mail(
        subject=f"Payment {status_value.capitalize()}",
        message=f"Your payment of ${payment.amount} has been {status_value}.",
        from_email='support@adcpa.live',
        recipient_list=[payment.user.email],
        fail_silently=False,
    )

    return Response({"message": f"Payment marked as {status_value}."})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_detail(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id, is_deleted=False)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

    if request.user.is_staff or request.user == payment.user:
        serializer = PaymentDetailSerializer(payment)
        return Response(serializer.data)
    return Response({"error": "Not authorized"}, status=403)


class PaymentFilter(filters.FilterSet):
    from_date = filters.DateFilter(field_name="created_at", lookup_expr='gte')
    to_date = filters.DateFilter(field_name="created_at", lookup_expr='lte')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = Payment
        fields = ['status', 'method', 'user__email', 'from_date', 'to_date', 'min_amount', 'max_amount']


class AllPaymentsView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = PaymentSerializer
    queryset = Payment.objects.filter(is_deleted=False).order_by('-created_at')
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentFilter


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_payment_summary(request):
    total = Payment.objects.filter(is_deleted=False).count()
    approved = Payment.objects.filter(is_deleted=False, status='approved').count()
    pending = Payment.objects.filter(is_deleted=False, status='pending').count()
    rejected = Payment.objects.filter(is_deleted=False, status='rejected').count()
    return Response({
        "total": total,
        "approved": approved,
        "pending": pending,
        "rejected": rejected,
    })


@api_view(['POST', 'PUT'])
@permission_classes([IsAuthenticated])
def save_billing_info(request):
    user = request.user
    data = request.data
    info, created = UserBillingInfo.objects.get_or_create(user=user)

    fields = ['account_number', 'bank_name', 'payment_email', 'wallet_address', 'crypto_network', 'currency']
    for field in fields:
        if field in data:
            setattr(info, field, data.get(field))

    info.save()
    return Response({"message": "Billing info saved successfully."})


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_payment(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        payment.delete()
        return Response({"message": "Payment soft-deleted."})
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_user_info(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        billing = UserBillingInfo.objects.filter(user=user).first()
        return Response({
            "email": user.email,
            "full_name": f"{user.first_name} {user.last_name}",
            "billing": {
                "account_number": billing.account_number if billing else "",
                "bank_name": billing.bank_name if billing else "",
                "payment_email": billing.payment_email if billing else "",
                "wallet_address": billing.wallet_address if billing else "",
                "crypto_network": billing.crypto_network if billing else "",
                "currency": billing.currency if billing else "USD"
            }
        })
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def generate_invoice(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{payment_id}.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, f"Invoice for Payment #{payment.id}")
    p.drawString(100, 780, f"User: {payment.user.email}")
    p.drawString(100, 760, f"Amount: ${payment.amount}")
    p.drawString(100, 740, f"Method: {payment.method}")
    p.drawString(100, 720, f"Status: {payment.status}")
    p.drawString(100, 700, f"Date: {payment.created_at.strftime('%Y-%m-%d')}")
    p.showPage()
    p.save()

    return response
