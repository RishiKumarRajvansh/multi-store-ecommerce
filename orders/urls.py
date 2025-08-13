from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/<uuid:store_id>/', views.cart_view, name='cart'),
    path('cart/<uuid:store_id>/add/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/<uuid:store_id>/update/', views.update_cart_view, name='update_cart'),
    path('cart/<uuid:store_id>/remove/', views.remove_from_cart_view, name='remove_from_cart'),
    path('checkout/<uuid:store_id>/', views.checkout_view, name='checkout'),
    path('order/<uuid:order_id>/', views.order_detail_view, name='order_detail'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
]