"""
Hospital App Admin
"""
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import Hospital, HospitalDataset, Doctor
from heartfl.admin import heartfl_admin_site


class HospitalAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'contact_number', 'verify_status', 'created_at']
    list_filter = ['is_verified', 'state', 'created_at']
    search_fields = ['name', 'city', 'registration_number', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'registration_number')
        }),
        ('Contact Details', {
            'fields': ('email', 'contact_number')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'pincode')
        }),
        ('Status', {
            'fields': ('is_verified',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_hospitals', 'unverify_hospitals']
    
    def verify_status(self, obj):
        """Display verification status with color"""
        if obj.is_verified:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Verified</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Unverified</span>'
        )
    verify_status.short_description = "Status"
    
    def verify_hospitals(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f"✓ {count} hospital(s) verified successfully.", messages.SUCCESS)
    verify_hospitals.short_description = "✓ Verify selected hospitals"
    
    def unverify_hospitals(self, request, queryset):
        count = queryset.update(is_verified=False)
        self.message_user(request, f"✗ {count} hospital(s) unverified.", messages.WARNING)
    unverify_hospitals.short_description = "✗ Unverify selected hospitals"


class HospitalDatasetAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'filename', 'num_records', 'uploaded_at', 'process_status']
    list_filter = ['is_processed', 'uploaded_at', 'hospital']
    search_fields = ['hospital__name', 'description']
    readonly_fields = ['uploaded_at']
    date_hierarchy = 'uploaded_at'
    
    def filename(self, obj):
        return obj.filename()
    
    def process_status(self, obj):
        """Display processing status"""
        if obj.is_processed:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Processed</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
        )
    process_status.short_description = "Status"
    
    fieldsets = (
        ('Hospital', {
            'fields': ('hospital',)
        }),
        ('Dataset Information', {
            'fields': ('dataset_file', 'num_records', 'description')
        }),
        ('Status', {
            'fields': ('is_processed', 'uploaded_at')
        }),
    )


class DoctorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'hospital', 'specialization', 'email', 'active_status', 'created_at']
    list_filter = ['is_active', 'hospital', 'specialization', 'created_at']
    search_fields = ['full_name', 'email', 'license_number', 'hospital__name']
    readonly_fields = ['created_at', 'updated_at']
    
    actions = [
        'activate_doctors',
        'deactivate_doctors',
    ]
    
    def active_status(self, obj):
        """Display activity status"""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">● Active</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">● Inactive</span>'
        )
    active_status.short_description = "Status"
    
    def activate_doctors(self, request, queryset):
        """Activate selected doctors"""
        count = queryset.update(is_active=True)
        self.message_user(request, f"✓ {count} doctor(s) activated.", messages.SUCCESS)
    activate_doctors.short_description = "✓ Activate selected doctors"
    
    def deactivate_doctors(self, request, queryset):
        """Deactivate selected doctors"""
        count = queryset.update(is_active=False)
        self.message_user(request, f"✗ {count} doctor(s) deactivated.", messages.WARNING)
    deactivate_doctors.short_description = "✗ Deactivate selected doctors"
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('full_name', 'specialization')
        }),
        ('Hospital', {
            'fields': ('hospital',)
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Professional', {
            'fields': ('license_number',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Register with custom admin site
heartfl_admin_site.register(Hospital, HospitalAdmin)
heartfl_admin_site.register(HospitalDataset, HospitalDatasetAdmin)
heartfl_admin_site.register(Doctor, DoctorAdmin)
