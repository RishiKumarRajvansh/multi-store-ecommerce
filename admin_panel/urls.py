from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard_view, name='dashboard'),
    path('stores/', views.stores_management_view, name='stores'),
    path('orders/', views.orders_management_view, name='orders'),
    path('chat-monitoring/', views.chat_monitoring_view, name='chat_monitoring'),
    path('closure-requests/', views.closure_requests_view, name='closure_requests'),
]