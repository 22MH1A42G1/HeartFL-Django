"""
Federated Learning App Admin
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import FederatedRound, LocalModel
from heartfl.admin import heartfl_admin_site


class FederatedRoundAdmin(admin.ModelAdmin):
    list_display = ['round_number', 'participating_hospitals', 'accuracy_display', 'completion_status', 'started_at']
    list_filter = ['is_completed', 'started_at']
    search_fields = ['round_number', 'description']
    readonly_fields = ['started_at']
    date_hierarchy = 'started_at'
    
    def accuracy_display(self, obj):
        """Display accuracy with color coding"""
        accuracy = obj.global_accuracy
        if accuracy >= 0.8:
            color = "green"
        elif accuracy >= 0.7:
            color = "orange"
        else:
            color = "red"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2%}</span>',
            color,
            accuracy
        )
    accuracy_display.short_description = "Accuracy"
    
    def completion_status(self, obj):
        """Display completion status"""
        if obj.is_completed:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Completed</span>'
            )
        return format_html(
            '<span style="color: blue; font-weight: bold;">⏳ In Progress</span>'
        )
    completion_status.short_description = "Status"
    
    fieldsets = (
        ('Round Information', {
            'fields': ('round_number', 'description')
        }),
        ('Metrics', {
            'fields': ('global_accuracy', 'global_loss', 'participating_hospitals')
        }),
        ('Status', {
            'fields': ('is_completed', 'started_at', 'completed_at')
        }),
    )


class LocalModelAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'federated_round', 'accuracy_display', 'training_samples', 'upload_status', 'training_started']
    list_filter = ['is_uploaded', 'hospital', 'federated_round', 'training_started']
    search_fields = ['hospital__name']
    readonly_fields = ['training_started']
    date_hierarchy = 'training_started'
    
    def accuracy_display(self, obj):
        """Display accuracy with color coding"""
        accuracy = obj.accuracy
        if accuracy >= 0.8:
            color = "green"
        elif accuracy >= 0.7:
            color = "orange"
        else:
            color = "red"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.2%}</span>',
            color,
            accuracy
        )
    accuracy_display.short_description = "Accuracy"
    
    def upload_status(self, obj):
        """Display upload status"""
        if obj.is_uploaded:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Uploaded</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Not Uploaded</span>'
        )
    upload_status.short_description = "Upload Status"
    
    fieldsets = (
        ('Hospital & Round', {
            'fields': ('hospital', 'federated_round')
        }),
        ('Training Metrics', {
            'fields': ('accuracy', 'loss', 'training_samples', 'epochs_trained')
        }),
        ('Status', {
            'fields': ('is_uploaded', 'training_started', 'training_completed')
        }),
    )


# Register with custom admin site
heartfl_admin_site.register(FederatedRound, FederatedRoundAdmin)
heartfl_admin_site.register(LocalModel, LocalModelAdmin)
