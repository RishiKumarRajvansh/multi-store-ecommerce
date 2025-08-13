from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, OTPVerification, UserLoginHistory


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'phone_number', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_phone_verified', 'is_email_verified')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'role', 'is_phone_verified', 'is_email_verified', 
                      'profile_picture', 'date_of_birth', 'last_login_ip')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'role', 'first_name', 'last_name')
        }),
    )


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'otp_type', 'phone_number', 'email', 'is_verified', 'created_at')
    list_filter = ('otp_type', 'is_verified', 'created_at')
    search_fields = ('user__username', 'phone_number', 'email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(UserLoginHistory)
class UserLoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'is_successful', 'created_at')
    list_filter = ('is_successful', 'created_at')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('created_at',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
