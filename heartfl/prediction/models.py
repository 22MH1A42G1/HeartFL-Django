"""
Prediction Models
Manages patient data and prediction results
"""
from django.db import models
from hospitals.models import Doctor


class PatientData(models.Model):
    """
    Patient health data for heart disease prediction
    Contains all features required by the ML model
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    
    CHEST_PAIN_CHOICES = [
        (0, 'Typical Angina'),
        (1, 'Atypical Angina'),
        (2, 'Non-anginal Pain'),
        (3, 'Asymptomatic'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patients')
    patient_name = models.CharField(max_length=200)
    age = models.IntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    
    # Clinical features for heart disease prediction
    chest_pain_type = models.IntegerField(choices=CHEST_PAIN_CHOICES)
    resting_bp = models.IntegerField(help_text="Resting Blood Pressure (mm Hg)")
    cholesterol = models.IntegerField(help_text="Serum Cholesterol (mg/dl)")
    fasting_bs = models.BooleanField(default=False, help_text="Fasting Blood Sugar > 120 mg/dl")
    resting_ecg = models.IntegerField(default=0, help_text="Resting ECG results (0-2)")
    max_heart_rate = models.IntegerField(help_text="Maximum Heart Rate Achieved")
    exercise_angina = models.BooleanField(default=False, help_text="Exercise Induced Angina")
    oldpeak = models.FloatField(help_text="ST Depression Induced by Exercise")
    st_slope = models.IntegerField(default=0, help_text="Slope of Peak Exercise ST Segment (0-2)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Patient Data'
        verbose_name_plural = 'Patient Data Records'
    
    def __str__(self):
        return f"{self.patient_name} - {self.age} years ({self.gender})"


class PredictionResult(models.Model):
    """
    Stores heart disease prediction results
    Links patient data with prediction outcomes
    """
    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('high', 'High Risk'),
    ]
    
    patient_data = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name='predictions')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='predictions')
    
    # Prediction results
    prediction = models.CharField(max_length=10, choices=RISK_LEVELS)
    probability = models.FloatField(help_text="Probability of heart disease (0-100%)")
    confidence_score = models.FloatField(default=0.0)
    
    # Model information
    model_version = models.CharField(max_length=50, default='v1.0')
    
    # Metadata
    predicted_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="Doctor's notes")
    
    class Meta:
        ordering = ['-predicted_at']
        verbose_name = 'Prediction Result'
        verbose_name_plural = 'Prediction Results'
    
    def __str__(self):
        return f"{self.patient_data.patient_name} - {self.prediction} ({self.probability:.2f}%)"
    
    def get_risk_class(self):
        """Return CSS class for risk level"""
        return 'danger' if self.prediction == 'high' else 'success'
