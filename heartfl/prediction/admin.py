"""
Prediction App Admin
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import PatientData, PredictionResult
from heartfl.admin import heartfl_admin_site


class PatientDataAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'age', 'gender', 'doctor', 'created_at']
    list_filter = ['gender', 'created_at', 'doctor__hospital']
    search_fields = ['patient_name', 'doctor__full_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Doctor', {
            'fields': ('doctor',)
        }),
        ('Patient Information', {
            'fields': ('patient_name', 'age', 'gender')
        }),
        ('Clinical Features', {
            'fields': (
                'chest_pain_type', 'resting_bp', 'cholesterol',
                'fasting_bs', 'resting_ecg', 'max_heart_rate',
                'exercise_angina', 'oldpeak', 'st_slope'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class PredictionResultAdmin(admin.ModelAdmin):
    list_display = ['patient_data', 'doctor', 'prediction_result', 'probability', 'predicted_at']
    list_filter = ['prediction', 'predicted_at', 'doctor__hospital']
    search_fields = ['patient_data__patient_name', 'doctor__full_name']
    readonly_fields = ['predicted_at']
    date_hierarchy = 'predicted_at'
    
    def prediction_result(self, obj):
        """Display prediction with color coding"""
        if obj.prediction == 'Yes':
            return format_html(
                '<span style="color: red; font-weight: bold; background: #ffe6e6; padding: 5px; border-radius: 3px;">⚠ At Risk</span>'
            )
        return format_html(
            '<span style="color: green; font-weight: bold; background: #e6ffe6; padding: 5px; border-radius: 3px;">✓ Healthy</span>'
        )
    prediction_result.short_description = "Prediction"
    
    fieldsets = (
        ('Patient & Doctor', {
            'fields': ('patient_data', 'doctor')
        }),
        ('Prediction Results', {
            'fields': ('prediction', 'probability', 'confidence_score')
        }),
        ('Model Information', {
            'fields': ('model_version',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamp', {
            'fields': ('predicted_at',)
        }),
    )


# Register with custom admin site
heartfl_admin_site.register(PatientData, PatientDataAdmin)
heartfl_admin_site.register(PredictionResult, PredictionResultAdmin)
