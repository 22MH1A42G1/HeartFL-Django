"""
Custom Admin Site Configuration for HeartFL
Provides enhanced admin interface with branding and customization
"""
from django.contrib import admin


class HeartFLAdminSite(admin.AdminSite):
    """Custom admin site for HeartFL with enhanced branding"""
    
    site_header = "🏥 HeartFL Administration"
    site_title = "HeartFL Admin Portal"
    index_title = "Dashboard"
    
    enable_nav_sidebar = True
    
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }
    
    def index(self, request, extra_context=None):
        """Dashboard with statistics"""
        extra_context = extra_context or {}
        
        try:
            from django.contrib.auth.models import User
            from hospitals.models import Hospital, HospitalDataset, Doctor
            from accounts.models import UserProfile
            from core.models import ContactMessage
            
            extra_context.update({
                'total_users': User.objects.count(),
                'total_hospitals': Hospital.objects.count(),
                'verified_hospitals': Hospital.objects.filter(is_verified=True).count(),
                'total_doctors': Doctor.objects.count(),
                'active_doctors': Doctor.objects.filter(is_active=True).count(),
                'total_datasets': HospitalDataset.objects.count(),
                'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
                'total_profiles': UserProfile.objects.count(),
            })
        except Exception:
            pass
        
        return super().index(request, extra_context)


# Create custom admin site instance
heartfl_admin_site = HeartFLAdminSite(name='heartfl_admin')
