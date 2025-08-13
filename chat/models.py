from django.db import models
from django.utils import timezone
from core.models import TimestampedModel
import uuid


class ChatSession(TimestampedModel):
    """Chat session between customer and store."""
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
        ('admin_taken_over', 'Admin Taken Over'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='customer_chat_sessions'
    )
    store = models.ForeignKey(
        'stores.Store', 
        on_delete=models.CASCADE, 
        related_name='chat_sessions'
    )
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='chat_sessions',
        null=True,
        blank=True
    )
    
    subject = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Admin oversight
    admin_user = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='supervised_chat_sessions'
    )
    escalated_at = models.DateTimeField(null=True, blank=True)
    admin_takeover_at = models.DateTimeField(null=True, blank=True)
    
    # Session metadata
    is_anonymous = models.BooleanField(default=False)
    customer_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Closure information
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='closed_chat_sessions'
    )
    closure_reason = models.TextField(blank=True)
    
    # Ratings
    customer_rating = models.PositiveIntegerField(null=True, blank=True)
    customer_feedback = models.TextField(blank=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['store']),
            models.Index(fields=['order']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Chat #{str(self.id)[:8]} - {self.customer.username} & {self.store.name}"
    
    @property
    def is_active(self):
        """Check if chat session is still active."""
        return self.status == 'active'
    
    @property
    def last_message_time(self):
        """Get timestamp of last message."""
        last_message = self.messages.order_by('-created_at').first()
        return last_message.created_at if last_message else self.created_at
    
    @property
    def unread_count_for_customer(self):
        """Count unread messages for customer."""
        return self.messages.filter(
            sender_role__in=['store', 'admin'],
            is_read_by_customer=False
        ).count()
    
    @property
    def unread_count_for_store(self):
        """Count unread messages for store."""
        return self.messages.filter(
            sender_role='customer',
            is_read_by_store=False
        ).count()


class ChatMessage(TimestampedModel):
    """Individual chat messages."""
    
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('file', 'File'),
        ('system', 'System'),
        ('order_update', 'Order Update'),
    )
    
    SENDER_ROLES = (
        ('customer', 'Customer'),
        ('store', 'Store'),
        ('admin', 'Admin'),
        ('system', 'System'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='sent_chat_messages',
        null=True,
        blank=True
    )
    sender_role = models.CharField(max_length=10, choices=SENDER_ROLES)
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    attachment_name = models.CharField(max_length=255, blank=True)
    
    # Message status
    is_read_by_customer = models.BooleanField(default=False)
    is_read_by_store = models.BooleanField(default=False)
    is_read_by_admin = models.BooleanField(default=False)
    
    read_by_customer_at = models.DateTimeField(null=True, blank=True)
    read_by_store_at = models.DateTimeField(null=True, blank=True)
    read_by_admin_at = models.DateTimeField(null=True, blank=True)
    
    # Message metadata
    reply_to = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='replies'
    )
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session']),
            models.Index(fields=['sender']),
            models.Index(fields=['created_at']),
            models.Index(fields=['message_type']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender_role} at {self.created_at}"
    
    def mark_as_read(self, reader_role):
        """Mark message as read by specific role."""
        now = timezone.now()
        if reader_role == 'customer' and not self.is_read_by_customer:
            self.is_read_by_customer = True
            self.read_by_customer_at = now
        elif reader_role == 'store' and not self.is_read_by_store:
            self.is_read_by_store = True
            self.read_by_store_at = now
        elif reader_role == 'admin' and not self.is_read_by_admin:
            self.is_read_by_admin = True
            self.read_by_admin_at = now
        self.save()


class ChatNotification(TimestampedModel):
    """Chat notifications for users."""
    
    NOTIFICATION_TYPES = (
        ('new_message', 'New Message'),
        ('session_closed', 'Session Closed'),
        ('admin_joined', 'Admin Joined'),
        ('escalated', 'Escalated'),
    )
    
    recipient = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='chat_notifications'
    )
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.ForeignKey(
        ChatMessage, 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True,
        blank=True
    )
    
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient']),
            models.Index(fields=['session']),
            models.Index(fields=['is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"


class Dispute(TimestampedModel):
    """Customer disputes and issues."""
    
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
    )
    
    DISPUTE_TYPES = (
        ('order_issue', 'Order Issue'),
        ('delivery_problem', 'Delivery Problem'),
        ('payment_issue', 'Payment Issue'),
        ('quality_complaint', 'Quality Complaint'),
        ('refund_request', 'Refund Request'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dispute_number = models.CharField(max_length=50, unique=True)
    
    customer = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='disputes'
    )
    store = models.ForeignKey(
        'stores.Store', 
        on_delete=models.CASCADE, 
        related_name='disputes'
    )
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='disputes',
        null=True,
        blank=True
    )
    chat_session = models.OneToOneField(
        ChatSession, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='dispute'
    )
    
    dispute_type = models.CharField(max_length=20, choices=DISPUTE_TYPES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    
    # Evidence
    evidence_files = models.JSONField(default=list, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_disputes'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    
    # Resolution
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    compensation_amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    class Meta:
        db_table = 'chat_disputes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dispute_number']),
            models.Index(fields=['customer']),
            models.Index(fields=['store']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Dispute #{self.dispute_number} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.dispute_number:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.dispute_number = f"DISP{timestamp}{str(uuid.uuid4())[:4].upper()}"
        super().save(*args, **kwargs)


class Resolution(TimestampedModel):
    """Dispute resolution records."""
    
    RESOLUTION_TYPES = (
        ('refund', 'Refund'),
        ('replacement', 'Replacement'),
        ('store_credit', 'Store Credit'),
        ('partial_refund', 'Partial Refund'),
        ('no_action', 'No Action'),
        ('other', 'Other'),
    )
    
    dispute = models.OneToOneField(
        Dispute, 
        on_delete=models.CASCADE, 
        related_name='resolution'
    )
    resolution_type = models.CharField(max_length=20, choices=RESOLUTION_TYPES)
    description = models.TextField()
    amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    resolved_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='resolved_disputes'
    )
    customer_satisfied = models.BooleanField(null=True, blank=True)
    customer_feedback = models.TextField(blank=True)
    
    class Meta:
        db_table = 'chat_resolutions'
    
    def __str__(self):
        return f"Resolution for {self.dispute.dispute_number}"
