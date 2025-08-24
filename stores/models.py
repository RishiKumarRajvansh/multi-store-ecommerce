from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import TimestampedModel, SoftDeleteModel, Address
import uuid


class Store(SoftDeleteModel):
    """Store model with all store information."""
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending_approval', 'Pending Approval'),
        ('suspended', 'Suspended'),
        ('temporarily_closed', 'Temporarily Closed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    store_code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='owned_stores'
    )
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    
    # Store branding
    logo = models.ImageField(upload_to='store_logos/', null=True, blank=True)
    banner_image = models.ImageField(upload_to='store_banners/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#007bff')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#6c757d')
    
    # Business information
    gstin = models.CharField(max_length=15, blank=True)
    fssai_license = models.CharField(max_length=14, blank=True)
    business_license = models.CharField(max_length=50, blank=True)
    
    # Operational information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_approval')
    is_active = models.BooleanField(default=True)
    min_order_amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    delivery_fee = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    free_delivery_threshold = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    
    # Timing
    opens_at = models.TimeField()
    closes_at = models.TimeField()
    is_24_hours = models.BooleanField(default=False)
    
    # Ratings and metrics
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    class Meta:
        db_table = 'stores_stores'
        indexes = [
            models.Index(fields=['store_code']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.store_code})"
    
    @property
    def is_open_now(self):
        """Check if store is currently open."""
        if not self.is_active or self.status != 'active':
            return False
        
        if self.is_24_hours:
            return True
            
        current_time = timezone.now().time()
        if self.opens_at <= self.closes_at:
            return self.opens_at <= current_time <= self.closes_at
        else:  # Store closes after midnight
            return current_time >= self.opens_at or current_time <= self.closes_at


class StoreStaff(TimestampedModel):
    """Store staff members with roles."""
    
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('cashier', 'Cashier'),
        ('inventory', 'Inventory Manager'),
        ('delivery_coordinator', 'Delivery Coordinator'),
    )
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='staff_members')
    user = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='store_assignments'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    permissions = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    hired_at = models.DateField()
    hourly_rate = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    class Meta:
        db_table = 'stores_staff'
        unique_together = ['store', 'user']
    
    def __str__(self):
        return f"{self.user.full_name} - {self.store.name} ({self.get_role_display()})"


class StoreZipCoverage(TimestampedModel):
    """Store delivery coverage for specific ZIP codes."""
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE, 
        related_name='zip_coverages'
    )
    zip_area = models.ForeignKey(
        'locations.ZipArea', 
        on_delete=models.CASCADE, 
        related_name='store_coverages'
    )
    delivery_fee = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text="Override store's default delivery fee for this ZIP"
    )
    min_order_amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text="Override store's default minimum order amount for this ZIP"
    )
    estimated_delivery_time_minutes = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'stores_zip_coverage'
        unique_together = ['store', 'zip_area']
        indexes = [
            models.Index(fields=['zip_area', 'is_active']),
            models.Index(fields=['store', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.store.name} - {self.zip_area.zip_code}"
    
    @property
    def effective_delivery_fee(self):
        """Get the effective delivery fee for this coverage."""
        return self.delivery_fee if self.delivery_fee is not None else self.store.delivery_fee
    
    @property
    def effective_min_order_amount(self):
        """Get the effective minimum order amount for this coverage."""
        return self.min_order_amount if self.min_order_amount is not None else self.store.min_order_amount


class StoreClosureRequest(TimestampedModel):
    """Store closure requests that need admin approval."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE, 
        related_name='closure_requests'
    )
    requested_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='store_closure_requests'
    )
    reason = models.TextField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    is_emergency = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    approved_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='approved_closure_requests'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'stores_closure_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.store.name} - {self.get_status_display()}"
    
    @property
    def is_active_closure(self):
        """Check if this is an active approved closure."""
        if self.status != 'approved':
            return False
        
        now = timezone.now()
        if self.end_datetime:
            return self.start_datetime <= now <= self.end_datetime
        else:
            return now >= self.start_datetime


class StoreHour(TimestampedModel):
    """Custom store hours for different days."""
    
    WEEKDAYS = (
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    )
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_hours')
    day = models.CharField(max_length=10, choices=WEEKDAYS)
    opens_at = models.TimeField()
    closes_at = models.TimeField()
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'stores_hours'
        unique_together = ['store', 'day']
    
    def __str__(self):
        if self.is_closed:
            return f"{self.store.name} - {self.get_day_display()}: Closed"
        return f"{self.store.name} - {self.get_day_display()}: {self.opens_at} - {self.closes_at}"
