from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import TimestampedModel, Address
import uuid


class DeliveryAgent(TimestampedModel):
    """Delivery agents assigned to stores."""
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_break', 'On Break'),
        ('off_duty', 'Off Duty'),
    )
    
    VEHICLE_TYPES = (
        ('bike', 'Bike'),
        ('scooter', 'Scooter'),
        ('car', 'Car'),
        ('bicycle', 'Bicycle'),
        ('walk', 'Walking'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='delivery_agent'
    )
    store = models.ForeignKey(
        'stores.Store', 
        on_delete=models.CASCADE, 
        related_name='delivery_agents'
    )
    
    # Agent details
    agent_code = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=15)
    
    # Vehicle information
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='bike')
    vehicle_number = models.CharField(max_length=20, blank=True)
    vehicle_documents = models.JSONField(default=dict, blank=True)
    
    # Status and location
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')
    current_latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    current_longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    last_location_update = models.DateTimeField(null=True, blank=True)
    
    # Performance metrics
    total_deliveries = models.PositiveIntegerField(default=0)
    successful_deliveries = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    average_delivery_time_minutes = models.PositiveIntegerField(default=0)
    
    # Financial
    commission_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        help_text="Commission per delivery"
    )
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'delivery_agents'
        indexes = [
            models.Index(fields=['agent_code']),
            models.Index(fields=['store']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} ({self.agent_code}) - {self.store.name}"
    
    @property
    def success_rate(self):
        """Calculate delivery success rate."""
        if self.total_deliveries == 0:
            return 0
        return (self.successful_deliveries / self.total_deliveries) * 100
    
    @property
    def is_online(self):
        """Check if agent is currently online."""
        return (self.status in ['active', 'on_break'] and 
                self.last_location_update and 
                (timezone.now() - self.last_location_update).seconds < 300)  # 5 minutes


class DeliveryAssignment(TimestampedModel):
    """Assignment of orders to delivery agents."""
    
    STATUS_CHOICES = (
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='delivery_assignment'
    )
    agent = models.ForeignKey(
        DeliveryAgent, 
        on_delete=models.CASCADE, 
        related_name='assignments'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')
    
    # Timestamps
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Estimated times
    estimated_pickup_time = models.DateTimeField(null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    
    # Distance and time
    pickup_distance_km = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    delivery_distance_km = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    actual_delivery_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Notes and feedback
    agent_notes = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    customer_rating = models.PositiveIntegerField(
        null=True, 
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    customer_feedback = models.TextField(blank=True)
    
    class Meta:
        db_table = 'delivery_assignments'
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['agent']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_at']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.agent.user.full_name}"


class DeliveryTracking(TimestampedModel):
    """Real-time delivery tracking updates."""
    assignment = models.ForeignKey(
        DeliveryAssignment, 
        on_delete=models.CASCADE, 
        related_name='tracking_updates'
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy_meters = models.PositiveIntegerField(null=True, blank=True)
    speed_kmh = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    bearing_degrees = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    class Meta:
        db_table = 'delivery_tracking'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assignment']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.assignment.order.order_number} tracking at {self.created_at}"


class ProofOfDelivery(TimestampedModel):
    """Proof of delivery with photos and signatures."""
    
    VERIFICATION_METHODS = (
        ('photo', 'Photo'),
        ('otp', 'OTP'),
        ('signature', 'Signature'),
        ('contactless', 'Contactless'),
    )
    
    assignment = models.OneToOneField(
        DeliveryAssignment, 
        on_delete=models.CASCADE, 
        related_name='proof_of_delivery'
    )
    verification_method = models.CharField(max_length=20, choices=VERIFICATION_METHODS)
    
    # Photo evidence
    delivery_photo = models.ImageField(
        upload_to='delivery_proofs/', 
        null=True, 
        blank=True
    )
    recipient_photo = models.ImageField(
        upload_to='delivery_proofs/', 
        null=True, 
        blank=True
    )
    
    # OTP verification
    otp_code = models.CharField(max_length=10, blank=True)
    otp_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Signature
    signature_data = models.TextField(blank=True, help_text="Base64 encoded signature")
    
    # Recipient information
    recipient_name = models.CharField(max_length=100, blank=True)
    recipient_phone = models.CharField(max_length=15, blank=True)
    delivery_notes = models.TextField(blank=True)
    
    # Location verification
    delivery_latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    delivery_longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    location_accuracy_meters = models.PositiveIntegerField(null=True, blank=True)
    
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'delivery_proof_of_delivery'
    
    def __str__(self):
        return f"Proof for {self.assignment.order.order_number}"


class DeliveryRoute(TimestampedModel):
    """Optimized delivery routes for agents."""
    agent = models.ForeignKey(
        DeliveryAgent, 
        on_delete=models.CASCADE, 
        related_name='routes'
    )
    date = models.DateField()
    route_name = models.CharField(max_length=100, blank=True)
    
    # Route optimization data
    total_distance_km = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    estimated_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    route_coordinates = models.JSONField(
        default=list,
        help_text="Array of [lat, lng] coordinates for the route"
    )
    
    # Route status
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'delivery_routes'
        unique_together = ['agent', 'date', 'route_name']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.agent.user.full_name} - {self.date} Route"


class DeliveryRouteStop(TimestampedModel):
    """Individual stops in a delivery route."""
    route = models.ForeignKey(
        DeliveryRoute, 
        on_delete=models.CASCADE, 
        related_name='stops'
    )
    assignment = models.ForeignKey(
        DeliveryAssignment, 
        on_delete=models.CASCADE, 
        related_name='route_stops'
    )
    stop_order = models.PositiveIntegerField()
    
    # Stop details
    estimated_arrival = models.DateTimeField()
    actual_arrival = models.DateTimeField(null=True, blank=True)
    estimated_duration_minutes = models.PositiveIntegerField(default=5)
    actual_duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'delivery_route_stops'
        unique_together = ['route', 'assignment']
        ordering = ['stop_order']
    
    def __str__(self):
        return f"{self.route} - Stop {self.stop_order}: {self.assignment.order.order_number}"
