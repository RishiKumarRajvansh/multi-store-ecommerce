from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from locations.models import ZipArea
from stores.models import Store, StoreZipCoverage


def zip_code_entry_view(request):
    """Landing page for ZIP code entry."""
    if request.method == 'POST':
        zip_code = request.POST.get('zip_code', '').strip()
        if zip_code:
            # Check if ZIP code is serviceable
            try:
                zip_area = ZipArea.objects.get(zip_code=zip_code, is_serviceable=True)
                # Store ZIP code in session
                request.session['zip_code'] = zip_code
                return redirect('home', zip_code=zip_code)
            except ZipArea.DoesNotExist:
                messages.error(request, f"Sorry, we don't deliver to {zip_code} yet. We're expanding soon!")
        else:
            messages.error(request, "Please enter a valid ZIP code.")
    
    return render(request, 'core/zip_entry.html')


@cache_page(60 * 5)  # Cache for 5 minutes
def home_view(request, zip_code):
    """Home page showing stores serving the given ZIP code."""
    # Validate ZIP code
    try:
        zip_area = ZipArea.objects.get(zip_code=zip_code, is_serviceable=True)
    except ZipArea.DoesNotExist:
        messages.error(request, f"ZIP code {zip_code} is not serviceable.")
        return redirect('zip_entry')
    
    # Get stores serving this ZIP code
    store_coverages = StoreZipCoverage.objects.filter(
        zip_area=zip_area,
        is_active=True,
        store__is_active=True,
        store__status='active'
    ).select_related('store').order_by('store__name')
    
    stores_data = []
    for coverage in store_coverages:
        store = coverage.store
        # Check if store is currently open
        is_open = store.is_open_now
        
        stores_data.append({
            'store': store,
            'coverage': coverage,
            'is_open': is_open,
            'delivery_fee': coverage.effective_delivery_fee,
            'min_order': coverage.effective_min_order_amount,
            'estimated_time': coverage.estimated_delivery_time_minutes,
        })
    
    context = {
        'zip_area': zip_area,
        'stores_data': stores_data,
        'zip_code': zip_code,
    }
    
    return render(request, 'core/home.html', context)


def check_zip_availability(request):
    """AJAX endpoint to check ZIP code availability."""
    if request.method == 'GET':
        zip_code = request.GET.get('zip_code', '').strip()
        if zip_code:
            try:
                zip_area = ZipArea.objects.get(zip_code=zip_code, is_serviceable=True)
                store_count = zip_area.available_stores_count
                return JsonResponse({
                    'available': True,
                    'area_name': zip_area.area_name,
                    'city': zip_area.city,
                    'store_count': store_count,
                })
            except ZipArea.DoesNotExist:
                return JsonResponse({
                    'available': False,
                    'message': f"We don't deliver to {zip_code} yet."
                })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
