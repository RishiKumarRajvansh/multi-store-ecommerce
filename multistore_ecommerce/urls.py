"""
URL configuration for multistore_ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home_view, zip_code_entry_view, check_zip_availability

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', zip_code_entry_view, name='zip_entry'),
    path('home/<str:zip_code>/', home_view, name='home'),
    path('core/check-zip/', check_zip_availability, name='check_zip'),
    path('accounts/', include('accounts.urls')),
    path('stores/', include('stores.urls')),
    path('catalog/', include('catalog.urls')),
    path('orders/', include('orders.urls')),
    path('delivery/', include('delivery.urls')),
    path('chat/', include('chat.urls')),
    path('admin-panel/', include('admin_panel.urls')),
    path('payments/', include('payments.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
