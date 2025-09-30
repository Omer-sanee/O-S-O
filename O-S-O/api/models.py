from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, unique=True)
    country_code = models.CharField(max_length=5, blank=True)
    calling_code = models.CharField(max_length=5, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    display_name = models.CharField(max_length=30, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_profile_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.display_name or self.user.email} - {self.phone}"

    def save(self, *args, **kwargs):
        # Auto-set profile complete if display_name is provided
        if self.display_name and len(self.display_name.strip()) >= 2:
            self.is_profile_complete = True
        super().save(*args, **kwargs)


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """OTP expires after 2 minutes"""
        return timezone.now() > self.created_at + timedelta(minutes=2)

    def __str__(self):
        return f"OTP for {self.user.email} - {self.code}"
