"""
Prediction Forms
Patient data input form for heart disease prediction
"""
from django import forms
from .models import PatientData, PredictionResult


class PatientDataForm(forms.ModelForm):
    """
    Patient health data input form
    Collects all features required for heart disease prediction
    """
    
    class Meta:
        model = PatientData
        fields = [
            'patient_name', 'age', 'gender',
            'chest_pain_type', 'resting_bp', 'cholesterol',
            'fasting_bs', 'resting_ecg', 'max_heart_rate',
            'exercise_angina', 'oldpeak', 'st_slope'
        ]
        
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Patient Name'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age',
                'min': 1,
                'max': 120
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'chest_pain_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'resting_bp': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resting Blood Pressure (mm Hg)',
                'min': 50,
                'max': 250
            }),
            'cholesterol': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Serum Cholesterol (mg/dl)',
                'min': 100,
                'max': 600
            }),
            'fasting_bs': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'resting_ecg': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                (0, 'Normal'),
                (1, 'ST-T wave abnormality'),
                (2, 'Left ventricular hypertrophy')
            ]),
            'max_heart_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum Heart Rate',
                'min': 60,
                'max': 220
            }),
            'exercise_angina': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'oldpeak': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'ST Depression (0-10)',
                'step': '0.1',
                'min': 0,
                'max': 10
            }),
            'st_slope': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                (0, 'Upsloping'),
                (1, 'Flat'),
                (2, 'Downsloping')
            ]),
        }
        
        labels = {
            'patient_name': 'Patient Name',
            'age': 'Age (years)',
            'gender': 'Gender',
            'chest_pain_type': 'Chest Pain Type',
            'resting_bp': 'Resting Blood Pressure',
            'cholesterol': 'Cholesterol Level',
            'fasting_bs': 'Fasting Blood Sugar > 120 mg/dl',
            'resting_ecg': 'Resting ECG Results',
            'max_heart_rate': 'Maximum Heart Rate',
            'exercise_angina': 'Exercise Induced Angina',
            'oldpeak': 'ST Depression (Oldpeak)',
            'st_slope': 'ST Slope',
        }
