"""
Context processors for core app
Adds global variables to all templates
"""
from core.models import ContactMessage
from accounts.models import UserThemeSettings


def unread_messages(request):
    """
    Add unread contact messages count to all templates
    Only visible to staff/superusers
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        try:
            count = ContactMessage.objects.filter(is_read=False).count()
            return {'unread_messages_count': count}
        except Exception:
            return {'unread_messages_count': 0}
    return {'unread_messages_count': 0}


def theme_settings(request):
    """
    Add user's custom theme settings to all templates
    Allows customization of dark & light mode colors
    """
    theme_settings_obj = None
    if request.user.is_authenticated:
        try:
            theme_settings_obj = UserThemeSettings.objects.get(user=request.user)
        except UserThemeSettings.DoesNotExist:
            # Create default theme settings for new users
            theme_settings_obj = UserThemeSettings.objects.create(user=request.user)
    
    return {
        'user_theme_settings': theme_settings_obj
    }
