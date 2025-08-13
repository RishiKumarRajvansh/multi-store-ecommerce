from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from core.models import TimestampedModel, Address
import uuid


class User(AbstractUser):
    """Extended User model with additional fields."""
    
    USER_ROLES = (
        ('customer', 'Customer'),
        ('store_owner', 'Store Owner'),
        ('store_staff', 'Store Staff'),
        ('delivery_agent', 'Delivery Agent'),
        ('admin', 'Admin'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='customer')
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(TimestampedModel):
    """Extended profile information for users."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    preferred_language = models.CharField(max_length=10, default='en')
    notification_preferences = models.JSONField(default=dict)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    class Meta:
        db_table = 'accounts_user_profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class OTPVerification(TimestampedModel):
    """OTP verification for phone and email."""
    
    OTP_TYPES = (
        ('phone', 'Phone Verification'),
        ('email', 'Email Verification'),
        ('password_reset', 'Password Reset'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_verifications')
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES)
    otp_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=3)
    
    class Meta:
        db_table = 'accounts_otp_verifications'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_otp_type_display()}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_expired and not self.is_verified and self.attempts < self.max_attempts


class UserLoginHistory(TimestampedModel):
    """Track user login history."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(max_length=200, blank=True)
    is_successful = models.BooleanField(default=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'accounts_login_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"
