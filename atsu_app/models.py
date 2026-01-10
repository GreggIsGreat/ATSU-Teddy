from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with upload tracking"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    uploads_remaining = models.IntegerField(default=3)
    total_uploads = models.IntegerField(default=0)
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def can_upload(self):
        """Check if user can upload"""
        return self.uploads_remaining > 0 or self.is_premium

    def use_upload(self):
        """Decrement upload count and return success status"""
        if self.is_premium:
            self.total_uploads += 1
            self.save()
            return True, self.uploads_remaining

        if self.uploads_remaining > 0:
            self.uploads_remaining -= 1
            self.total_uploads += 1
            self.save()
            return True, self.uploads_remaining

        return False, 0

    def add_uploads(self, count):
        """Add uploads (for purchased bundles)"""
        self.uploads_remaining += count
        self.save()
        return self.uploads_remaining

    def reset_uploads(self, count=3):
        """Reset uploads to specific count"""
        self.uploads_remaining = count
        self.save()


# Auto-create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


class AnonymousUploadTracker(models.Model):
    """Track uploads for anonymous users by session and IP"""
    session_key = models.CharField(max_length=255, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    browser_fingerprint = models.CharField(max_length=255, null=True, blank=True)
    uploads_remaining = models.IntegerField(default=3)
    total_uploads = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['session_key', 'ip_address']

    def __str__(self):
        return f"Anonymous ({self.ip_address}): {self.uploads_remaining} remaining"

    def can_upload(self):
        return self.uploads_remaining > 0

    def use_upload(self):
        if self.uploads_remaining > 0:
            self.uploads_remaining -= 1
            self.total_uploads += 1
            self.save()
            return True, self.uploads_remaining
        return False, 0


class UploadHistory(models.Model):
    """Track all uploads for analytics"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploads')
    anonymous_tracker = models.ForeignKey(AnonymousUploadTracker, on_delete=models.SET_NULL, null=True, blank=True)
    cv_filename = models.CharField(max_length=255)
    jd_filename = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Store analysis results reference
    analysis_id = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=50, default='pending')  # pending, processing, completed, failed

    def __str__(self):
        owner = self.user.username if self.user else f"Anonymous ({self.ip_address})"
        return f"Upload by {owner} at {self.created_at}"