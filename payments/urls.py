from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('process/<uuid:order_id>/', views.process_payment_view, name='process'),
    path('callback/', views.payment_callback_view, name='callback'),
    path('success/<uuid:payment_id>/', views.payment_success_view, name='success'),
    path('failed/<uuid:payment_id>/', views.payment_failed_view, name='failed'),
]