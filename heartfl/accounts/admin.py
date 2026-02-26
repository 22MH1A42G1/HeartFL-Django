"""
Accounts App Admin
"""
from django.contrib import admin
from .models import UserProfile
from heartfl.admin import heartfl_admin_site


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'phone', 'created_at']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('user_type', 'phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request):
        """Prevent deletion of user profiles"""
        return request.user.is_superuser


# Register with custom admin site
heartfl_admin_site.register(UserProfile, UserProfileAdmin)
