from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from core.models import TimestampedModel
import uuid


class PaymentMethod(TimestampedModel):
    """Payment methods supported by the platform."""
    
    METHOD_TYPES = (
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('net_banking', 'Net Banking'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
        ('cash_on_delivery', 'Cash on Delivery'),
        ('emi', 'EMI'),
    )
    
    name = models.CharField(max_length=100)
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='payment_icons/', null=True, blank=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    processing_fee_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    processing_fee_fixed = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    
    # Limits
    min_amount = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    max_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    display_order = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'payments_methods'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return self.name


class Payment(TimestampedModel):
    """Payment records for orders."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_id = models.CharField(max_length=100, unique=True)
    
    # Order relationship
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    
    # Payment details
    payment_method = models.ForeignKey(
        PaymentMethod, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Amounts
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    processing_fee = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Gateway details
    gateway_payment_id = models.CharField(max_length=200, blank=True)
    gateway_order_id = models.CharField(max_length=200, blank=True)
    gateway_signature = models.CharField(max_length=500, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Failure information
    failure_reason = models.TextField(blank=True)
    failure_code = models.CharField(max_length=50, blank=True)
    
    # Refund information
    refund_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    customer_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payments_payments'
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['payment_id']),
            models.Index(fields=['order']),
            models.Index(fields=['status']),
            models.Index(fields=['initiated_at']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_id} - {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.payment_id:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.payment_id = f"PAY{timestamp}{str(uuid.uuid4())[:8].upper()}"
        
        # Calculate total amount
        self.total_amount = self.amount + self.processing_fee
        super().save(*args, **kwargs)
    
    @property
    def is_successful(self):
        """Check if payment was successful."""
        return self.status == 'success'
    
    @property
    def can_be_refunded(self):
        """Check if payment can be refunded."""
        return (self.status == 'success' and 
                self.refund_amount < self.total_amount)


class PaymentAttempt(TimestampedModel):
    """Track payment attempts for debugging."""
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.CASCADE, 
        related_name='attempts'
    )
    attempt_number = models.PositiveIntegerField()
    
    # Request data
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    
    # Status
    is_successful = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    error_code = models.CharField(max_length=50, blank=True)
    
    # Timing
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'payments_attempts'
        unique_together = ['payment', 'attempt_number']
        ordering = ['attempt_number']
    
    def __str__(self):
        return f"{self.payment.payment_id} - Attempt {self.attempt_number}"


class Refund(TimestampedModel):
    """Refund records."""
    
    STATUS_CHOICES = (
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    REFUND_TYPES = (
        ('full', 'Full Refund'),
        ('partial', 'Partial Refund'),
        ('processing_fee', 'Processing Fee Refund'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    refund_id = models.CharField(max_length=100, unique=True)
    
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.CASCADE, 
        related_name='refunds'
    )
    refund_type = models.CharField(max_length=20, choices=REFUND_TYPES, default='full')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='initiated')
    
    # Amounts
    refund_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    
    # Refund details
    reason = models.TextField()
    initiated_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='initiated_refunds'
    )
    
    # Gateway details
    gateway_refund_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Failure information
    failure_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'payments_refunds'
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['refund_id']),
            models.Index(fields=['payment']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Refund {self.refund_id} - ₹{self.refund_amount}"
    
    def save(self, *args, **kwargs):
        if not self.refund_id:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.refund_id = f"REF{timestamp}{str(uuid.uuid4())[:6].upper()}"
        super().save(*args, **kwargs)


class Wallet(TimestampedModel):
    """User wallet for storing credits."""
    user = models.OneToOneField(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'payments_wallets'
    
    def __str__(self):
        return f"{self.user.username} Wallet - ₹{self.balance}"
    
    def add_money(self, amount, description=""):
        """Add money to wallet."""
        if amount > 0:
            self.balance += amount
            self.save()
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type='credit',
                amount=amount,
                description=description,
                balance_after=self.balance
            )
    
    def deduct_money(self, amount, description=""):
        """Deduct money from wallet."""
        if amount > 0 and self.balance >= amount:
            self.balance -= amount
            self.save()
            WalletTransaction.objects.create(
                wallet=self,
                transaction_type='debit',
                amount=amount,
                description=description,
                balance_after=self.balance
            )
            return True
        return False


class WalletTransaction(TimestampedModel):
    """Wallet transaction history."""
    
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    )
    
    wallet = models.ForeignKey(
        Wallet, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    description = models.TextField(blank=True)
    balance_before = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Reference information
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='wallet_transactions'
    )
    refund = models.ForeignKey(
        Refund, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='wallet_transactions'
    )
    
    class Meta:
        db_table = 'payments_wallet_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet']),
            models.Index(fields=['created_at']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        return f"{self.wallet.user.username} - {self.get_transaction_type_display()} ₹{self.amount}"
