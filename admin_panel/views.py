from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages


@staff_member_required
def admin_dashboard_view(request):
    """Admin dashboard view."""
    return render(request, 'admin_panel/dashboard.html')


@staff_member_required
def stores_management_view(request):
    """Stores management view."""
    return render(request, 'admin_panel/stores.html')


@staff_member_required
def orders_management_view(request):
    """Orders management view."""
    return render(request, 'admin_panel/orders.html')


@staff_member_required
def chat_monitoring_view(request):
    """Chat monitoring view."""
    return render(request, 'admin_panel/chat_monitoring.html')


@staff_member_required
def closure_requests_view(request):
    """Store closure requests view."""
    return render(request, 'admin_panel/closure_requests.html')
