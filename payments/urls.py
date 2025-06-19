from django.urls import path
from . import views

urlpatterns = [
    path('admin/all/', views.AllPaymentsView.as_view(), name='admin-all-payments'),
    path('admin/summary/', views.admin_payment_summary),
    path('create/', views.create_payment_request),
    path('my/', views.user_payments),
    path('all/', views.all_payments),
    path('update/<int:payment_id>/', views.update_payment_status),
    path('delete/<int:payment_id>/', views.delete_payment),
    path('save-billing-info/', views.save_billing_info),
    path('user/<int:user_id>/', views.get_user_info),
    path('invoice/<int:payment_id>/', views.generate_invoice),
    path('<int:payment_id>/', views.payment_detail),  # 🔚 সবশেষে রাখুন
]
