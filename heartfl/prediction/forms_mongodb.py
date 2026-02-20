"""
Prediction Forms - MONGODB INTEGRATED
======================================
"""
from django import forms


class PatientDataForm(forms.Form):
    """
    Patient clinical data form for heart disease prediction.
    
    11 FEATURES from standard heart disease dataset.
    """
    
    age = forms.IntegerField(
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Age in years'
        })
    )
    
    sex = forms.ChoiceField(
        choices=[
            (0, 'Female'),
            (1, 'Male')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    chest_pain_type = forms.ChoiceField(
        label='Chest Pain Type',
        choices=[
            (0, 'Typical Angina'),
            (1, 'Atypical Angina'),
            (2, 'Non-anginal Pain'),
            (3, 'Asymptomatic')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    resting_bp = forms.IntegerField(
        label='Resting Blood Pressure (mm Hg)',
        min_value=0,
        max_value=300,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 120'
        })
    )
    
    cholesterol = forms.IntegerField(
        label='Cholesterol (mg/dl)',
        min_value=0,
        max_value=600,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 200'
        })
    )
    
    fasting_bs = forms.ChoiceField(
        label='Fasting Blood Sugar > 120 mg/dl',
        choices=[
            (0, 'No'),
            (1, 'Yes')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    resting_ecg = forms.ChoiceField(
        label='Resting ECG Results',
        choices=[
            (0, 'Normal'),
            (1, 'ST-T Wave Abnormality'),
            (2, 'Left Ventricular Hypertrophy')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    max_heart_rate = forms.IntegerField(
        label='Maximum Heart Rate',
        min_value=0,
        max_value=220,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 150'
        })
    )
    
    exercise_angina = forms.ChoiceField(
        label='Exercise Induced Angina',
        choices=[
            (0, 'No'),
            (1, 'Yes')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    oldpeak = forms.FloatField(
        label='ST Depression (Oldpeak)',
        min_value=0.0,
        max_value=10.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 1.5',
            'step': '0.1'
        })
    )
    
    st_slope = forms.ChoiceField(
        label='ST Slope',
        choices=[
            (0, 'Upsloping'),
            (1, 'Flat'),
            (2, 'Downsloping')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
