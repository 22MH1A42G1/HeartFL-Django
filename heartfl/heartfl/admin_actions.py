"""
Custom Admin Actions for Database Management
Provides bulk operations, export, and cleanup actions
"""
from django.contrib import messages
from django.http import HttpResponse
from heartfl.db_management import DatabaseUtilities
from datetime import datetime


def export_as_csv(modeladmin, request, queryset):
    """Admin action: Export selected items as CSV"""
    try:
        response = DatabaseUtilities.export_to_csv(queryset)
        if response:
            return response
        modeladmin.message_user(request, "No data to export.", messages.WARNING)
    except Exception as e:
        modeladmin.message_user(request, f"Error exporting data: {str(e)}", messages.ERROR)
export_as_csv.short_description = "📥 Export selected as CSV"


def export_as_json(modeladmin, request, queryset):
    """Admin action: Export selected items as JSON"""
    try:
        response = DatabaseUtilities.export_to_json(queryset)
        if response:
            return response
        modeladmin.message_user(request, "No data to export.", messages.WARNING)
    except Exception as e:
        modeladmin.message_user(request, f"Error exporting data: {str(e)}", messages.ERROR)
export_as_json.short_description = "📥 Export selected as JSON"


def delete_selected_soft(modeladmin, request, queryset):
    """Admin action: Soft delete (mark as inactive if available)"""
    updated = 0
    
    for obj in queryset:
        if hasattr(obj, 'is_active'):
            obj.is_active = False
            obj.save()
            updated += 1
        elif hasattr(obj, 'is_verified'):
            obj.is_verified = False
            obj.save()
            updated += 1
    
    if updated > 0:
        modeladmin.message_user(
            request, 
            f"✓ {updated} record(s) marked as inactive/unverified.",
            messages.SUCCESS
        )
    else:
        modeladmin.message_user(
            request,
            "No compatible records found for soft delete.",
            messages.WARNING
        )
delete_selected_soft.short_description = "🔒 Mark selected as inactive"


def duplicate_selected(modeladmin, request, queryset):
    """Admin action: Duplicate selected items"""
    duplicated = 0
    
    for obj in queryset:
        obj.pk = None
        obj.id = None
        obj.save()
        duplicated += 1
    
    modeladmin.message_user(
        request,
        f"✓ {duplicated} record(s) duplicated successfully.",
        messages.SUCCESS
    )
duplicate_selected.short_description = "📋 Duplicate selected records"


def get_summary_stats(modeladmin, request, queryset):
    """Get summary statistics for queryset"""
    count = queryset.count()
    model_name = queryset.model.__name__
    
    message = f"📊 {model_name}: {count} record(s) selected"
    modeladmin.message_user(request, message, messages.INFO)
get_summary_stats.short_description = "📊 Show statistics"


# Common admin actions list
COMMON_ACTIONS = [
    export_as_csv,
    export_as_json,
    delete_selected_soft,
    duplicate_selected,
    get_summary_stats,
]
