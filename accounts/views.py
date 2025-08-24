from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User, OTPVerification
import random
import string
from datetime import datetime, timedelta


def register_view(request):
    """User registration view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role', 'customer')
        
        # Basic validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        elif User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already exists.')
        else:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('accounts:login')
    
    return render(request, 'accounts/register.html')


def login_view(request):
    """User login view."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', 'zip_entry')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('zip_entry')


@login_required
def profile_view(request):
    """User profile view."""
    return render(request, 'accounts/profile.html', {'user': request.user})


def verify_otp_view(request):
    """OTP verification view."""
    return render(request, 'accounts/verify_otp.html')
