from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import Category, Product


def categories_view(request):
    """Categories listing view."""
    categories = Category.objects.filter(is_active=True, parent=None).order_by('display_order', 'name')
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'catalog/categories.html', context)


def product_detail_view(request, product_id):
    """Product detail view."""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    context = {
        'product': product,
    }
    
    return render(request, 'catalog/product_detail.html', context)


def search_view(request):
    """Product search view."""
    query = request.GET.get('q', '')
    products = []
    
    if query:
        products = Product.objects.filter(
            name__icontains=query,
            is_active=True
        ).order_by('name')
    
    context = {
        'query': query,
        'products': products,
    }
    
    return render(request, 'catalog/search.html', context)
