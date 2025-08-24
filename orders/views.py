from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem, Order


@login_required
def cart_view(request, store_id):
    """Cart view for specific store."""
    return render(request, 'orders/cart.html', {'store_id': store_id})


@login_required  
def add_to_cart_view(request, store_id):
    """Add item to cart."""
    if request.method == 'POST':
        return JsonResponse({'success': True, 'message': 'Item added to cart'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required
def update_cart_view(request, store_id):
    """Update cart item quantity."""
    return JsonResponse({'success': True, 'message': 'Cart updated'})


@login_required
def remove_from_cart_view(request, store_id):
    """Remove item from cart."""
    return JsonResponse({'success': True, 'message': 'Item removed'})


@login_required
def checkout_view(request, store_id):
    """Checkout view."""
    return render(request, 'orders/checkout.html', {'store_id': store_id})


@login_required
def order_detail_view(request, order_id):
    """Order detail view."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def my_orders_view(request):
    """User's orders listing."""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})
