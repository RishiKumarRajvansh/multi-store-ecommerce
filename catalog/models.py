from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from core.models import TimestampedModel, SoftDeleteModel
import uuid


class Category(TimestampedModel):
    """Product categories."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories'
    )
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'catalog_categories'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    @property
    def full_path(self):
        """Get full category path."""
        path = [self.name]
        parent = self.parent
        while parent:
            path.append(parent.name)
            parent = parent.parent
        return " > ".join(reversed(path))


class Product(SoftDeleteModel):
    """Global product master data."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Product specifications
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    
    # Physical properties
    weight_grams = models.PositiveIntegerField(null=True, blank=True)
    dimensions = models.JSONField(null=True, blank=True, help_text="Length, width, height in cm")
    
    # Product images
    main_image = models.ImageField(upload_to='product_images/')
    additional_images = models.JSONField(default=list, blank=True)
    
    # SEO and metadata
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Product attributes
    is_vegetarian = models.BooleanField(default=False)
    shelf_life_days = models.PositiveIntegerField(null=True, blank=True)
    storage_temperature = models.CharField(max_length=50, blank=True)
    preparation_time_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    # Nutritional information (per 100g)
    calories_per_100g = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    protein_per_100g = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    fat_per_100g = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    carbs_per_100g = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'catalog_products'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class StoreProduct(TimestampedModel):
    """Store-specific product information including pricing and inventory."""
    store = models.ForeignKey(
        'stores.Store', 
        on_delete=models.CASCADE, 
        related_name='store_products'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_products')
    
    # Pricing
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    compare_at_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Original price for showing discounts"
    )
    cost_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    max_quantity_per_order = models.PositiveIntegerField(null=True, blank=True)
    
    # Store-specific attributes
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    
    # Store-specific customizations
    store_description = models.TextField(blank=True)
    store_images = models.JSONField(default=list, blank=True)
    
    class Meta:
        db_table = 'catalog_store_products'
        unique_together = ['store', 'product']
        indexes = [
            models.Index(fields=['store', 'is_available']),
            models.Index(fields=['product']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"{self.store.name} - {self.product.name}"
    
    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        """Check if product is low in stock."""
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_at_price is set."""
        if self.compare_at_price and self.compare_at_price > self.price:
            return ((self.compare_at_price - self.price) / self.compare_at_price) * 100
        return 0


class Ingredient(TimestampedModel):
    """Add-on ingredients for products."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    is_vegetarian = models.BooleanField(default=True)
    calories_per_unit = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'catalog_ingredients'
    
    def __str__(self):
        return self.name


class ProductIngredient(TimestampedModel):
    """Available ingredients for products."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='available_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='products')
    is_required = models.BooleanField(default=False)
    default_quantity = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_quantity = models.DecimalField(max_digits=5, decimal_places=2, default=5)
    
    class Meta:
        db_table = 'catalog_product_ingredients'
        unique_together = ['product', 'ingredient']
    
    def __str__(self):
        return f"{self.product.name} - {self.ingredient.name}"


class ProductSuggestion(TimestampedModel):
    """Frequently bought together suggestions."""
    primary_product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='suggestions_as_primary'
    )
    suggested_product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='suggestions_as_suggested'
    )
    score = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Confidence score between 0 and 1"
    )
    times_bought_together = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'catalog_product_suggestions'
        unique_together = ['primary_product', 'suggested_product']
        indexes = [
            models.Index(fields=['primary_product', 'score']),
        ]
    
    def __str__(self):
        return f"{self.primary_product.name} -> {self.suggested_product.name}"


class ProductReview(TimestampedModel):
    """Product reviews and ratings."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    store = models.ForeignKey(
        'stores.Store', 
        on_delete=models.CASCADE, 
        related_name='product_reviews'
    )
    user = models.ForeignKey(
        'accounts.User', 
        on_delete=models.CASCADE, 
        related_name='product_reviews'
    )
    order = models.ForeignKey(
        'orders.Order', 
        on_delete=models.CASCADE, 
        related_name='product_reviews',
        null=True,
        blank=True
    )
    
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    images = models.JSONField(default=list, blank=True)
    
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    helpful_votes = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'catalog_product_reviews'
        unique_together = ['product', 'user', 'order']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.rating}★ by {self.user.username}"
