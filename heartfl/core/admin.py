"""
Core App Admin
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import ContactMessage
from heartfl.admin import heartfl_admin_site


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'submitted_at', 'read_status']
    list_filter = ['is_read', 'submitted_at']
    search_fields = ['name', 'email', 'phone', 'subject', 'message']
    readonly_fields = ['submitted_at']
    date_hierarchy = 'submitted_at'
    
    def read_status(self, obj):
        """Display read status with color"""
        if obj.is_read:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Read</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">● Unread</span>'
        )
    read_status.short_description = "Status"
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'submitted_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f"{count} message(s) marked as read.")
    mark_as_read.short_description = "✓ Mark selected as read"
    
    def mark_as_unread(self, request, queryset):
        count = queryset.update(is_read=False)
        self.message_user(request, f"{count} message(s) marked as unread.")
    mark_as_unread.short_description = "● Mark selected as unread"


# Register with custom admin site
heartfl_admin_site.register(ContactMessage, ContactMessageAdmin)
