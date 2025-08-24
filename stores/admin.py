from django.contrib import admin
from .models import Store, StoreStaff, StoreZipCoverage, StoreClosureRequest, StoreHour


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'store_code', 'owner', 'status', 'is_active', 'city', 'phone_number')
    list_filter = ('status', 'is_active', 'created_at')
    search_fields = ('name', 'store_code', 'owner__username', 'phone_number')
    readonly_fields = ('created_at', 'updated_at', 'total_orders', 'total_revenue')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'store_code', 'description', 'owner')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address')
        }),
        ('Business Information', {
            'fields': ('gstin', 'fssai_license', 'business_license')
        }),
        ('Branding', {
            'fields': ('logo', 'banner_image', 'primary_color', 'secondary_color')
        }),
        ('Operational Settings', {
            'fields': ('status', 'is_active', 'min_order_amount', 'delivery_fee', 
                      'free_delivery_threshold', 'opens_at', 'closes_at', 'is_24_hours')
        }),
        ('Metrics', {
            'fields': ('average_rating', 'total_orders', 'total_revenue'),
            'classes': ('collapse',)
        }),
    )
    
    def city(self, obj):
        return obj.address.city if obj.address else '-'
    city.short_description = 'City'


@admin.register(StoreStaff)
class StoreStaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'store', 'role', 'is_active', 'hired_at')
    list_filter = ('role', 'is_active', 'hired_at')
    search_fields = ('user__username', 'store__name')


@admin.register(StoreZipCoverage)
class StoreZipCoverageAdmin(admin.ModelAdmin):
    list_display = ('store', 'zip_area', 'delivery_fee', 'min_order_amount', 'estimated_delivery_time_minutes', 'is_active')
    list_filter = ('is_active', 'store')
    search_fields = ('store__name', 'zip_area__zip_code', 'zip_area__area_name')


@admin.register(StoreClosureRequest)
class StoreClosureRequestAdmin(admin.ModelAdmin):
    list_display = ('store', 'requested_by', 'status', 'is_emergency', 'start_datetime', 'created_at')
    list_filter = ('status', 'is_emergency', 'created_at')
    search_fields = ('store__name', 'requested_by__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Request Information', {
            'fields': ('store', 'requested_by', 'reason', 'is_emergency')
        }),
        ('Schedule', {
            'fields': ('start_datetime', 'end_datetime')
        }),
        ('Approval', {
            'fields': ('status', 'admin_notes', 'approved_by', 'approved_at')
        }),
    )


@admin.register(StoreHour)
class StoreHourAdmin(admin.ModelAdmin):
    list_display = ('store', 'day', 'opens_at', 'closes_at', 'is_closed')
    list_filter = ('day', 'is_closed')
    search_fields = ('store__name',)
