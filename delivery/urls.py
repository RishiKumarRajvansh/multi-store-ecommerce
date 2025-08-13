from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('track/<uuid:order_id>/', views.track_order_view, name='track_order'),
    path('agent-dashboard/', views.agent_dashboard_view, name='agent_dashboard'),
    path('update-location/', views.update_location_view, name='update_location'),
]