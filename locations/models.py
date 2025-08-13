from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import TimestampedModel


class ZipArea(TimestampedModel):
    """ZIP code areas with delivery information."""
    zip_code = models.CharField(max_length=10, unique=True)
    area_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_serviceable = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'locations_zip_areas'
        indexes = [
            models.Index(fields=['zip_code']),
            models.Index(fields=['city']),
            models.Index(fields=['is_serviceable']),
        ]
    
    def __str__(self):
        return f"{self.zip_code} - {self.area_name}, {self.city}"
    
    @property
    def available_stores_count(self):
        """Count of stores serving this ZIP code."""
        return self.store_coverages.filter(is_active=True, store__is_active=True).count()


class DeliveryZone(TimestampedModel):
    """Delivery zones for grouping ZIP codes."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    zip_areas = models.ManyToManyField(ZipArea, related_name='delivery_zones')
    base_delivery_fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'locations_delivery_zones'
    
    def __str__(self):
        return self.name


class DistanceMatrix(TimestampedModel):
    """Pre-calculated distances between locations."""
    from_zip = models.ForeignKey(
        ZipArea, 
        on_delete=models.CASCADE, 
        related_name='distances_from'
    )
    to_zip = models.ForeignKey(
        ZipArea, 
        on_delete=models.CASCADE, 
        related_name='distances_to'
    )
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    estimated_time_minutes = models.PositiveIntegerField()
    
    class Meta:
        db_table = 'locations_distance_matrix'
        unique_together = ['from_zip', 'to_zip']
        indexes = [
            models.Index(fields=['from_zip', 'to_zip']),
        ]
    
    def __str__(self):
        return f"{self.from_zip.zip_code} to {self.to_zip.zip_code}: {self.distance_km}km"


class ServiceableArea(TimestampedModel):
    """Define serviceable areas with custom boundaries."""
    name = models.CharField(max_length=100)
    polygon_coordinates = models.JSONField(
        help_text="Array of [lat, lng] coordinates defining the service area boundary"
    )
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6)
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'locations_serviceable_areas'
    
    def __str__(self):
        return self.name
