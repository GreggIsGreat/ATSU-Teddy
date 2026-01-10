"""
Upload Tracking Utility
Handles upload quota management for both authenticated and anonymous users
"""

from functools import wraps
from django.http import JsonResponse
from .models import UserProfile, AnonymousUploadTracker, UploadHistory


class UploadTracker:
    """
    Utility class for managing upload quotas
    Works for both authenticated and anonymous users
    """

    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def get_tracker(request):
        """
        Get the appropriate tracker for the request.
        Returns (tracker, tracker_type) tuple.
        tracker_type is 'user' or 'anonymous'
        """
        if request.user.is_authenticated:
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            return profile, 'user'
        else:
            # Ensure session exists
            if not request.session.session_key:
                request.session.create()

            session_key = request.session.session_key
            ip_address = UploadTracker.get_client_ip(request)

            # Try to find existing tracker
            # First by session
            tracker = AnonymousUploadTracker.objects.filter(session_key=session_key).first()

            if not tracker:
                # Check by IP address (prevents new browser bypass)
                tracker = AnonymousUploadTracker.objects.filter(ip_address=ip_address).first()

                if tracker:
                    # Update session key for this IP
                    tracker.session_key = session_key
                    tracker.save()
                else:
                    # Create new tracker
                    tracker = AnonymousUploadTracker.objects.create(
                        session_key=session_key,
                        ip_address=ip_address
                    )

            return tracker, 'anonymous'

    @staticmethod
    def can_upload(request):
        """Check if the current user/session can upload"""
        tracker, _ = UploadTracker.get_tracker(request)
        return tracker.can_upload()

    @staticmethod
    def get_remaining(request):
        """Get remaining uploads for current user/session"""
        tracker, _ = UploadTracker.get_tracker(request)
        return tracker.uploads_remaining

    @staticmethod
    def use_upload(request):
        """
        Use one upload from quota.
        Returns (success, remaining_count) tuple
        """
        tracker, _ = UploadTracker.get_tracker(request)
        return tracker.use_upload()

    @staticmethod
    def get_upload_context(request):
        """Get context dict for templates"""
        tracker, tracker_type = UploadTracker.get_tracker(request)
        return {
            'uploads_remaining': tracker.uploads_remaining,
            'can_upload': tracker.can_upload(),
            'is_premium': getattr(tracker, 'is_premium', False),
            'tracker_type': tracker_type,
        }

    @staticmethod
    def record_upload(request, cv_filename, jd_filename, analysis_id=None):
        """Record an upload in history"""
        tracker, tracker_type = UploadTracker.get_tracker(request)

        upload = UploadHistory.objects.create(
            user=request.user if request.user.is_authenticated else None,
            anonymous_tracker=tracker if tracker_type == 'anonymous' else None,
            cv_filename=cv_filename,
            jd_filename=jd_filename,
            ip_address=UploadTracker.get_client_ip(request),
            analysis_id=analysis_id,
            status='pending'
        )

        return upload


def require_upload_quota(view_func):
    """
    Decorator to check upload quota before allowing access to a view.
    Returns JSON error if no quota remaining.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not UploadTracker.can_upload(request):
            return JsonResponse({
                'success': False,
                'error': 'No uploads remaining. Please purchase a bundle.',
                'uploads_remaining': 0,
                'redirect_to_bundles': True
            }, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper