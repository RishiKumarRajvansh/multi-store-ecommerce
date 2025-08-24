from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('categories/', views.categories_view, name='categories'),
    path('products/<uuid:product_id>/', views.product_detail_view, name='product_detail'),
    path('search/', views.search_view, name='search'),
]