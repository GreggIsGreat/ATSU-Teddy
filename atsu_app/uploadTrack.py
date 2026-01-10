"""
Upload Tracking Module
Tracks the number of uploads per user and enforces upload limits.
"""

from django.core.cache import cache
from django.contrib.auth.models import User
from functools import wraps
from django.http import JsonResponse


class UploadTracker:
    """
    Tracks and manages user upload limits.
    """

    # Default upload limit per user
    DEFAULT_UPLOAD_LIMIT = 3

    # Cache timeout in seconds (24 hours)
    CACHE_TIMEOUT = 86400

    @staticmethod
    def get_cache_key(user_id):
        """Generate cache key for user upload count."""
        return f"upload_count_{user_id}"

    @staticmethod
    def get_remaining_uploads(user):
        """
        Get the number of remaining uploads for a user.

        Args:
            user: Django User object or user ID

        Returns:
            int: Number of remaining uploads
        """
        user_id = user.id if hasattr(user, 'id') else user
        cache_key = UploadTracker.get_cache_key(user_id)

        # Get current count from cache, default to 0
        current_count = cache.get(cache_key, 0)

        # Calculate remaining uploads
        remaining = UploadTracker.DEFAULT_UPLOAD_LIMIT - current_count
        return max(0, remaining)

    @staticmethod
    def can_upload(user):
        """
        Check if user can still upload documents.

        Args:
            user: Django User object or user ID

        Returns:
            bool: True if user can upload, False otherwise
        """
        return UploadTracker.get_remaining_uploads(user) > 0

    @staticmethod
    def increment_upload_count(user):
        """
        Increment the upload count for a user.

        Args:
            user: Django User object or user ID

        Returns:
            int: New upload count
        """
        user_id = user.id if hasattr(user, 'id') else user
        cache_key = UploadTracker.get_cache_key(user_id)

        # Get current count
        current_count = cache.get(cache_key, 0)

        # Increment count
        new_count = current_count + 1

        # Save to cache
        cache.set(cache_key, new_count, UploadTracker.CACHE_TIMEOUT)

        return new_count

    @staticmethod
    def reset_upload_count(user):
        """
        Reset the upload count for a user (admin function).

        Args:
            user: Django User object or user ID
        """
        user_id = user.id if hasattr(user, 'id') else user
        cache_key = UploadTracker.get_cache_key(user_id)
        cache.delete(cache_key)

    @staticmethod
    def get_upload_stats(user):
        """
        Get detailed upload statistics for a user.

        Args:
            user: Django User object or user ID

        Returns:
            dict: Dictionary with upload statistics
        """
        user_id = user.id if hasattr(user, 'id') else user
        cache_key = UploadTracker.get_cache_key(user_id)

        current_count = cache.get(cache_key, 0)
        remaining = UploadTracker.get_remaining_uploads(user)

        return {
            'total_limit': UploadTracker.DEFAULT_UPLOAD_LIMIT,
            'used': current_count,
            'remaining': remaining,
            'can_upload': remaining > 0,
            'percentage_used': (current_count / UploadTracker.DEFAULT_UPLOAD_LIMIT) * 100
        }


def require_upload_quota(view_func):
    """
    Decorator to check if user has remaining uploads before allowing access to view.

    Usage:
        @require_upload_quota
        def upload_view(request):
            # Your upload logic here
            pass
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required'
            }, status=401)

        if not UploadTracker.can_upload(request.user):
            return JsonResponse({
                'error': 'Upload limit reached',
                'message': 'You have reached your upload limit. Please contact support for more uploads.',
                'stats': UploadTracker.get_upload_stats(request.user)
            }, status=403)

        return view_func(request, *args, **kwargs)

    return wrapper


# Example usage in views.py:
"""
from .uploads_track import UploadTracker, require_upload_quota

@require_upload_quota
def upload_documents(request):
    if request.method == 'POST':
        # Process the upload
        # ... your upload logic ...

        # Increment the counter after successful upload
        UploadTracker.increment_upload_count(request.user)

        # Get remaining uploads to show user
        remaining = UploadTracker.get_remaining_uploads(request.user)

        return JsonResponse({
            'success': True,
            'remaining_uploads': remaining
        })

    return render(request, 'upload.html')


def upload_page(request):
    # Get upload stats for template context
    upload_stats = UploadTracker.get_upload_stats(request.user)

    return render(request, 'upload.html', {
        'upload_stats': upload_stats
    })
"""