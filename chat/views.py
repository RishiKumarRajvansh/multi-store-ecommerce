from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatSession


@login_required
def chat_sessions_view(request):
    """User's chat sessions."""
    sessions = ChatSession.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'chat/sessions.html', {'sessions': sessions})


@login_required
def chat_session_view(request, session_id):
    """Individual chat session view."""
    session = get_object_or_404(ChatSession, id=session_id)
    return render(request, 'chat/session.html', {'session': session})


@login_required
def start_chat_view(request):
    """Start new chat session."""
    return render(request, 'chat/start.html')


@login_required
def send_message_api(request):
    """API to send chat message."""
    return JsonResponse({'success': True})
