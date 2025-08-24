from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from orders.models import Order


def track_order_view(request, order_id):
    """Order tracking view."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'delivery/track_order.html', {'order': order})


@login_required
def agent_dashboard_view(request):
    """Delivery agent dashboard."""
    if request.user.role != 'delivery_agent':
        return redirect('home')
    return render(request, 'delivery/agent_dashboard.html')


@login_required
def update_location_view(request):
    """Update delivery agent location."""
    return JsonResponse({'success': True})
