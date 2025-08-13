from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_sessions_view, name='sessions'),
    path('session/<uuid:session_id>/', views.chat_session_view, name='session'),
    path('start/', views.start_chat_view, name='start'),
    path('api/send-message/', views.send_message_api, name='send_message'),
]