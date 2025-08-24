from django.urls import path
from . import views

app_name = 'stores'

urlpatterns = [
    path('<uuid:store_id>/', views.store_detail_view, name='detail'),
    path('<uuid:store_id>/products/', views.store_products_view, name='products'),
    path('<uuid:store_id>/products/<uuid:product_id>/', views.product_detail_view, name='product_detail'),
    path('dashboard/', views.store_dashboard_view, name='dashboard'),
    path('manage/', views.manage_store_view, name='manage'),
    path('closure-request/', views.closure_request_view, name='closure_request'),
]