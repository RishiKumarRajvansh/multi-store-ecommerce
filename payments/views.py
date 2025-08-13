from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from orders.models import Order
from .models import Payment


@login_required
def process_payment_view(request, order_id):
    """Process payment for order."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'payments/process.html', {'order': order})


def payment_callback_view(request):
    """Payment gateway callback."""
    return JsonResponse({'success': True})


def payment_success_view(request, payment_id):
    """Payment success view."""
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'payments/success.html', {'payment': payment})


def payment_failed_view(request, payment_id):
    """Payment failed view."""
    payment = get_object_or_404(Payment, id=payment_id)
    return render(request, 'payments/failed.html', {'payment': payment})
