from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_protect
from .uploadTrack import UploadTracker, require_upload_quota
from .models import UploadHistory
import os

"""
    Credentials:
    Username - ted_admin 
    Password - 1234
"""


# ══════════════════════════════════════════════════════════════
# PAGE VIEWS
# ══════════════════════════════════════════════════════════════

def index(request: HttpRequest) -> HttpResponse:
    """Home page with upload form"""
    context = UploadTracker.get_upload_context(request)
    return render(request, 'atsu_app/index.html', context)


def results(request: HttpRequest) -> HttpResponse:
    """Results/Analysis page"""
    context = UploadTracker.get_upload_context(request)
    return render(request, 'atsu_app/results.html', context)


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """User dashboard"""
    context = UploadTracker.get_upload_context(request)

    # Get user's upload history
    if request.user.is_authenticated:
        context['upload_history'] = UploadHistory.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]

    return render(request, 'atsu_app/dashboard.html', context)


def bundles(request: HttpRequest) -> HttpResponse:
    """Pricing/Bundles page"""
    context = UploadTracker.get_upload_context(request)
    return render(request, 'atsu_app/bundles.html', context)


# ══════════════════════════════════════════════════════════════
# AUTHENTICATION VIEWS
# ══════════════════════════════════════════════════════════════

def user_logout(request: HttpRequest) -> HttpResponse:
    """Log out the current user and redirect to index."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')


def sign_up(request: HttpRequest) -> HttpResponse:
    """Combined view for user registration and login."""
    context = UploadTracker.get_upload_context(request)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'register':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')

            if not all([username, email, password, password_confirm]):
                messages.error(request, 'All fields are required for registration.')
                return render(request, 'atsu_app/sign_up.html', context)

            if password != password_confirm:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'atsu_app/sign_up.html', context)

            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'atsu_app/sign_up.html', context)

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already registered.')
                return render(request, 'atsu_app/sign_up.html', context)

            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # Transfer anonymous uploads to new user if any remaining
                tracker, tracker_type = UploadTracker.get_tracker(request)
                if tracker_type == 'anonymous' and tracker.uploads_remaining < 3:
                    # User already used some uploads as anonymous
                    # Keep their remaining count
                    user.profile.uploads_remaining = tracker.uploads_remaining
                    user.profile.total_uploads = tracker.total_uploads
                    user.profile.save()

                messages.success(request, 'Registration successful! Please log in.')
                context['show_login'] = True
                return render(request, 'atsu_app/sign_up.html', context)
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                return render(request, 'atsu_app/sign_up.html', context)

        elif action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')

            if not all([username, password]):
                messages.error(request, 'Username and password are required.')
                context['show_login'] = True
                return render(request, 'atsu_app/sign_up.html', context)

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
                context['show_login'] = True
                return render(request, 'atsu_app/sign_up.html', context)

    return render(request, 'atsu_app/sign_up.html', context)


# ══════════════════════════════════════════════════════════════
# UPLOAD API ENDPOINTS
# ══════════════════════════════════════════════════════════════

@require_GET
def get_uploads_remaining(request: HttpRequest) -> JsonResponse:
    """API: Get remaining upload count"""
    tracker, tracker_type = UploadTracker.get_tracker(request)

    return JsonResponse({
        'success': True,
        'uploads_remaining': tracker.uploads_remaining,
        'can_upload': tracker.can_upload(),
        'is_premium': getattr(tracker, 'is_premium', False),
        'tracker_type': tracker_type
    })


@require_POST
@csrf_protect
def use_upload(request: HttpRequest) -> JsonResponse:
    """API: Decrement upload count (without file upload)"""
    tracker, tracker_type = UploadTracker.get_tracker(request)

    if not tracker.can_upload():
        return JsonResponse({
            'success': False,
            'error': 'No uploads remaining',
            'uploads_remaining': 0,
            'redirect_to_bundles': True
        }, status=403)

    success, remaining = tracker.use_upload()

    return JsonResponse({
        'success': success,
        'uploads_remaining': remaining,
        'can_upload': tracker.can_upload(),
    })


@require_POST
@csrf_protect
def submit_documents(request: HttpRequest) -> JsonResponse:
    """
    API: Handle document submission
    This is the main upload endpoint that:
    1. Validates files
    2. Checks upload quota
    3. Processes the upload
    4. Decrements the counter
    5. Returns result
    """
    tracker, tracker_type = UploadTracker.get_tracker(request)

    # Check quota first
    if not tracker.can_upload():
        return JsonResponse({
            'success': False,
            'error': 'No uploads remaining. Please purchase a bundle.',
            'uploads_remaining': 0,
            'redirect_to_bundles': True
        }, status=403)

    # Get uploaded files
    cv_file = request.FILES.get('cv')
    jd_file = request.FILES.get('job_description')

    # Validate files
    if not cv_file:
        return JsonResponse({
            'success': False,
            'error': 'CV file is required.'
        }, status=400)

    if not jd_file:
        return JsonResponse({
            'success': False,
            'error': 'Job Description file is required.'
        }, status=400)

    # Validate file types
    allowed_cv_types = ['.pdf', '.doc', '.docx']
    allowed_jd_types = ['.pdf', '.png', '.jpeg', '.jpg']

    cv_ext = os.path.splitext(cv_file.name)[1].lower()
    jd_ext = os.path.splitext(jd_file.name)[1].lower()

    if cv_ext not in allowed_cv_types:
        return JsonResponse({
            'success': False,
            'error': f'Invalid CV file type. Allowed: {", ".join(allowed_cv_types)}'
        }, status=400)

    if jd_ext not in allowed_jd_types:
        return JsonResponse({
            'success': False,
            'error': f'Invalid Job Description file type. Allowed: {", ".join(allowed_jd_types)}'
        }, status=400)

    # Validate file sizes (e.g., max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB

    if cv_file.size > max_size:
        return JsonResponse({
            'success': False,
            'error': 'CV file too large. Maximum size is 10MB.'
        }, status=400)

    if jd_file.size > max_size:
        return JsonResponse({
            'success': False,
            'error': 'Job Description file too large. Maximum size is 10MB.'
        }, status=400)

    try:
        # TODO: Add your file processing logic here
        # - Save files to storage (local, S3, etc.)
        # - Send to n8n workflow for analysis
        # - Get analysis ID back

        # For now, generate a placeholder analysis ID
        import uuid
        analysis_id = str(uuid.uuid4())[:8]

        # Record the upload
        upload_record = UploadTracker.record_upload(
            request=request,
            cv_filename=cv_file.name,
            jd_filename=jd_file.name,
            analysis_id=analysis_id
        )

        # Decrement upload count
        success, remaining = tracker.use_upload()

        if success:
            return JsonResponse({
                'success': True,
                'message': 'Documents submitted successfully!',
                'uploads_remaining': remaining,
                'can_upload': remaining > 0,
                'analysis_id': analysis_id,
                'redirect_to': f'/results/?id={analysis_id}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to process upload quota.',
                'uploads_remaining': remaining
            }, status=500)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }, status=500)


@require_POST
@csrf_protect
@login_required
def purchase_bundle(request: HttpRequest) -> JsonResponse:
    """API: Add uploads after purchase (placeholder for payment integration)"""
    bundle_type = request.POST.get('bundle')

    bundles = {
        'starter': 5,
        'professional': 15,
        'enterprise': 50,
    }

    uploads_to_add = bundles.get(bundle_type, 0)

    if uploads_to_add == 0:
        return JsonResponse({
            'success': False,
            'error': 'Invalid bundle type'
        }, status=400)

    # Add uploads to user profile
    profile = request.user.profile
    new_total = profile.add_uploads(uploads_to_add)

    return JsonResponse({
        'success': True,
        'message': f'Added {uploads_to_add} uploads to your account!',
        'uploads_remaining': new_total
    })