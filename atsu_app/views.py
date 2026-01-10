from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .uploadTrack import UploadTracker, require_upload_quota

"""
    Credentials:
    Username - ted_admin 
    Password - 1234
"""


# Create your views here.

def index(request: HttpRequest) -> HttpResponse:
    return render(request, 'atsu_app/index.html')

def results(request: HttpRequest) -> HttpResponse:
    return render(request, 'atsu_app/results.html')

def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, 'atsu_app/index.html')

def user_logout(request: HttpRequest) -> HttpResponse:
    """
    Log out the current user and redirect to index.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')


def sign_up(request: HttpRequest) -> HttpResponse:
    """
    Combined view for user registration and login using the same template.
    The form action determines which operation to perform.
    """
    if request.method == 'POST':
        action = request.POST.get('action')  # 'register' or 'login'

        if action == 'register':
            # Handle registration
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')

            # Validation
            if not all([username, email, password, password_confirm]):
                messages.error(request, 'All fields are required for registration.')
                return render(request, 'atsu_app/sign_up.html')

            if password != password_confirm:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'atsu_app/sign_up.html')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'atsu_app/sign_up.html')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
                return render(request, 'atsu_app/sign_up.html')

            # Create user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                messages.success(request, 'Registration successful! Please log in.')
                # Optionally auto-login the user:
                # login(request, user)
                # return redirect('index')
                return render(request, 'atsu_app/sign_up.html', {'show_login': True})
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                return render(request, 'atsu_app/sign_up.html')

        elif action == 'login':
            # Handle login
            username = request.POST.get('username')
            password = request.POST.get('password')

            if not all([username, password]):
                messages.error(request, 'Username and password are required.')
                return render(request, 'atsu_app/sign_up.html', {'show_login': True})

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
                return render(request, 'atsu_app/sign_up.html', {'show_login': True})

    return render(request, 'atsu_app/sign_up.html')


def bundles(request: HttpRequest) -> HttpResponse:
    return render(request, 'atsu_app/bundles.html')

def results(request: HttpRequest) -> HttpResponse:
    return render(request, 'atsu_app/results.html')