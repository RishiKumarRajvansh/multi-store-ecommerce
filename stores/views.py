from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Store, StoreZipCoverage, StoreClosureRequest
from catalog.models import StoreProduct, Category
from locations.models import ZipArea


def store_detail_view(request, store_id):
    """Store detail view."""
    store = get_object_or_404(Store, id=store_id)
    zip_code = request.session.get('zip_code')
    
    if not zip_code:
        return redirect('zip_entry')
    
    # Check if store serves this ZIP
    try:
        zip_area = ZipArea.objects.get(zip_code=zip_code)
        coverage = StoreZipCoverage.objects.get(
            store=store, 
            zip_area=zip_area, 
            is_active=True
        )
    except (ZipArea.DoesNotExist, StoreZipCoverage.DoesNotExist):
        messages.error(request, 'This store does not serve your area.')
        return redirect('home', zip_code=zip_code)
    
    context = {
        'store': store,
        'coverage': coverage,
        'is_open': store.is_open_now,
        'zip_code': zip_code,
    }
    
    return render(request, 'stores/detail.html', context)


def store_products_view(request, store_id):
    """Store products listing."""
    store = get_object_or_404(Store, id=store_id)
    zip_code = request.session.get('zip_code')
    
    if not zip_code:
        return redirect('zip_entry')
    
    # Get store products
    products = StoreProduct.objects.filter(
        store=store,
        is_available=True,
        product__is_active=True
    ).select_related('product', 'product__category').order_by('product__name')
    
    # Filter by category if specified
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(product__category__slug=category_slug)
    
    # Get categories for filtering
    categories = Category.objects.filter(
        products__store_products__store=store,
        is_active=True
    ).distinct().order_by('name')
    
    context = {
        'store': store,
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'zip_code': zip_code,
    }
    
    return render(request, 'stores/products.html', context)


def product_detail_view(request, store_id, product_id):
    """Individual product detail view."""
    store = get_object_or_404(Store, id=store_id)
    store_product = get_object_or_404(
        StoreProduct, 
        store=store, 
        product_id=product_id,
        is_available=True
    )
    
    context = {
        'store': store,
        'store_product': store_product,
        'product': store_product.product,
    }
    
    return render(request, 'stores/product_detail.html', context)


@login_required
def store_dashboard_view(request):
    """Store owner dashboard."""
    if request.user.role not in ['store_owner', 'store_staff']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get user's stores
    if request.user.role == 'store_owner':
        stores = request.user.owned_stores.all()
    else:
        stores = Store.objects.filter(staff_members__user=request.user)
    
    context = {
        'stores': stores,
    }
    
    return render(request, 'stores/dashboard.html', context)


@login_required
def manage_store_view(request):
    """Store management view."""
    if request.user.role not in ['store_owner', 'store_staff']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    return render(request, 'stores/manage.html')


@login_required
def closure_request_view(request):
    """Store closure request view."""
    if request.user.role not in ['store_owner', 'store_staff']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.method == 'POST':
        # Handle closure request form
        pass
    
    return render(request, 'stores/closure_request.html')
