"""
Context processors for core app
Adds global variables to all templates
"""
from core.models import ContactMessage


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
