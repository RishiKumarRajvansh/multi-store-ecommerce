from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from core.models import TimestampedModel, Address
import uuid


class Cart(TimestampedModel):
    """User shopping cart - separate cart per store."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='carts'
    )
    store = models.ForeignKey(
        'stores.Store', 
        on_delete=models.CASCADE, 
        related_name='carts'
    )
    zip_area = models.ForeignKey(
        'locations.ZipArea', 
        on_delete=models.CASCADE, 
        related_name='carts'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'orders_carts'
        unique_together = ['user', 'store']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['store']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.store.name} Cart"
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return self.items.filter(is_active=True).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    @property
    def subtotal(self):
        """Calculate cart subtotal."""
        total = 0
        for item in self.items.filter(is_active=True):
            total += item.line_total
        return total
    
    @property
    def delivery_fee(self):
        """Get delivery fee for this cart."""
        coverage = self.store.zip_coverages.filter(
            zip_area=self.zip_area, 
            is_active=True
        ).first()
        if coverage:
            return coverage.effective_delivery_fee
        return self.store.delivery_fee
    
    @property
    def total_amount(self):
        """Calculate total amount including delivery fee."""
        subtotal = self.subtotal
        if (self.store.free_delivery_threshold and 
            subtotal >= self.store.free_delivery_threshold):
            return subtotal
        return subtotal + self.delivery_fee


class CartItem(TimestampedModel):
    """Items in shopping cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    store_product = models.ForeignKey(
        'catalog.StoreProduct', 
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'orders_cart_items'
        unique_together = ['cart', 'store_product']
    
    def save(self, *args, **kwargs):
        # Set unit price from store product when creating
        if not self.pk:
            self.unit_price = self.store_product.price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.cart.user.username} - {self.store_product.product.name} x{self.quantity}"
    
    @property
    def line_total(self):
        """Calculate total for this cart item."""
        total = self.quantity * self.unit_price
        # Add ingredient costs
        for cart_ingredient in self.cart_ingredients.all():
            total += cart_ingredient.total_price
        return total


class CartItemIngredient(TimestampedModel):
    """Ingredients added to cart items."""
    cart_item = models.ForeignKey(
        CartItem, 
        on_delete=models.CASCADE, 
        related_name='cart_ingredients'
    )
    ingredient = models.ForeignKey(
        'catalog.Ingredient', 
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.DecimalField(max_digits=5, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    
    class Meta:
        db_table = 'orders_cart_item_ingredients'
        unique_together = ['cart_item', 'ingredient']
    
    def save(self, *args, **kwargs):
        if not self.pk:
            self.unit_price = self.ingredient.price
        super().save(*args, **kwargs)
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price


class Order(TimestampedModel):
    """Customer orders."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('ready_for_pickup', 'Ready for Pickup'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True)
    
    # Customer information
    customer = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    store = models.ForeignKey(
        'stores.Store', 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    
    # Delivery information
    delivery_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    zip_area = models.ForeignKey(
        'locations.ZipArea', 
        on_delete=models.CASCADE, 
        related_name='orders'
    )
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending'
    )
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=6, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Special instructions
    customer_notes = models.TextField(blank=True)
    store_notes = models.TextField(blank=True)
    
    # Timestamps
    confirmed_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'orders_orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer']),
            models.Index(fields=['store']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number} - {self.customer.username}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.order_number = f"ORD{timestamp}{str(uuid.uuid4())[:6].upper()}"
        super().save(*args, **kwargs)


class OrderItem(TimestampedModel):
    """Items in an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    store_product = models.ForeignKey(
        'catalog.StoreProduct', 
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    product_name = models.CharField(max_length=200)  # Snapshot at time of order
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    
    class Meta:
        db_table = 'orders_order_items'
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product_name} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.store_product.product.name
        if not self.line_total:
            self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class OrderItemIngredient(TimestampedModel):
    """Ingredients for order items."""
    order_item = models.ForeignKey(
        OrderItem, 
        on_delete=models.CASCADE, 
        related_name='ingredients'
    )
    ingredient_name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    
    class Meta:
        db_table = 'orders_order_item_ingredients'
    
    def __str__(self):
        return f"{self.order_item.product_name} - {self.ingredient_name}"


class OrderStatusHistory(TimestampedModel):
    """Track order status changes."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='order_status_changes'
    )
    
    class Meta:
        db_table = 'orders_status_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status} at {self.created_at}"


class DeliverySlot(TimestampedModel):
    """Available delivery time slots."""
    store = models.ForeignKey(
        'stores.Store', 
        on_delete=models.CASCADE, 
        related_name='delivery_slots'
    )
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_orders = models.PositiveIntegerField(default=10)
    current_orders = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'orders_delivery_slots'
        unique_together = ['store', 'date', 'start_time']
        indexes = [
            models.Index(fields=['store', 'date']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.store.name} - {self.date} {self.start_time}-{self.end_time}"
    
    @property
    def is_available(self):
        """Check if slot has capacity."""
        return self.is_active and self.current_orders < self.max_orders
    
    @property
    def available_spots(self):
        """Number of available spots in this slot."""
        return max(0, self.max_orders - self.current_orders)
