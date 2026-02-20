"""
Accounts Models
User profile extensions for Hospital and Doctor roles
"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extended user profile to distinguish between Hospital and Doctor users
    """
    USER_TYPE_CHOICES = [
        ('hospital', 'Hospital'),
        ('doctor', 'Doctor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username} ({self.user_type})"
    
    def is_hospital(self):
        return self.user_type == 'hospital'
    
    def is_doctor(self):
        return self.user_type == 'doctor'
