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


class UserThemeSettings(models.Model):
    """
    User-customizable theme preferences for Dark & Light modes
    Stores custom color values for personalized UI experience
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='theme_settings')
    
    # Light Mode Colors
    light_bg_color = models.CharField(max_length=7, default='#E3F2FD', help_text='Light mode background color')
    light_text_color = models.CharField(max_length=7, default='#01579B', help_text='Light mode text color')
    light_accent_color = models.CharField(max_length=7, default='#0288D1', help_text='Light mode accent/primary color')
    light_card_bg = models.CharField(max_length=7, default='#FFFFFF', help_text='Light mode card background')
    
    # Dark Mode Colors
    dark_bg_color = models.CharField(max_length=7, default='#1B4332', help_text='Dark mode background color')
    dark_text_color = models.CharField(max_length=7, default='#D8F3DC', help_text='Dark mode text color')
    dark_accent_color = models.CharField(max_length=7, default='#52B788', help_text='Dark mode accent/primary color')
    dark_card_bg = models.CharField(max_length=7, default='#2D6A4F', help_text='Dark mode card background')
    
    # General Settings
    preferred_theme = models.CharField(
        max_length=10,
        choices=[('light', 'Light Mode'), ('dark', 'Dark Mode'), ('auto', 'Auto (System)')],
        default='auto',
        help_text='User preferred default theme'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Theme Settings'
        verbose_name_plural = 'User Theme Settings'
    
    def __str__(self):
        return f"Theme Settings for {self.user.username}"
    
    def get_light_theme_colors(self):
        """Return all light theme colors as dictionary"""
        return {
            'bg': self.light_bg_color,
            'text': self.light_text_color,
            'accent': self.light_accent_color,
            'card_bg': self.light_card_bg,
        }
    
    def get_dark_theme_colors(self):
        """Return all dark theme colors as dictionary"""
        return {
            'bg': self.dark_bg_color,
            'text': self.dark_text_color,
            'accent': self.dark_accent_color,
            'card_bg': self.dark_card_bg,
        }
