from django.db import models
from core.models import TimestampedModel


class DashboardMetric(TimestampedModel):
    """Admin dashboard metrics and KPIs."""
    
    METRIC_TYPES = (
        ('daily_orders', 'Daily Orders'),
        ('daily_revenue', 'Daily Revenue'),
        ('active_users', 'Active Users'),
        ('store_performance', 'Store Performance'),
        ('delivery_metrics', 'Delivery Metrics'),
    )
    
    metric_type = models.CharField(max_length=30, choices=METRIC_TYPES)
    date = models.DateField()
    value = models.DecimalField(max_digits=12, decimal_places=2)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'admin_dashboard_metrics'
        unique_together = ['metric_type', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.get_metric_type_display()} - {self.date}: {self.value}"


class AdminNotification(TimestampedModel):
    """Notifications for admin users."""
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Recipients
    recipient = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='admin_notifications',
        null=True,
        blank=True
    )
    is_broadcast = models.BooleanField(default=False)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Related objects
    related_model = models.CharField(max_length=50, blank=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'admin_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['is_read']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"
