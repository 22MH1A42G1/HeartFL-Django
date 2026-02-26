"""
MongoDB Document Models for Prediction App
===========================================

Stores patient clinical data and ML prediction results.

WHY MONGODB FOR PATIENT DATA:
- Medical records often have varying structures
- Easy to add new clinical parameters without migrations
- Document model matches medical record format
- Supports future extensions (lab results, imaging metadata)

PRIVACY & FL CONSIDERATIONS:
- Patient data linked to doctor AND hospital for traceability
- Enables hospital-specific analytics
- Supports federated learning by keeping data partitioned
"""

from mongoengine import (
    Document, StringField, IntField, FloatField, BooleanField,
    DateTimeField, ReferenceField
)
from datetime import datetime


class PatientData(Document):
    """
    Clinical data for heart disease prediction.
    
    11 FEATURES (Standard Heart Disease Dataset):
    1. age: Patient age in years
    2. sex: Gender (0=Female, 1=Male)
    3. chest_pain_type: 0-3 (Typical Angina, Atypical, Non-anginal, Asymptomatic)
    4. resting_bp: Resting blood pressure (mm Hg)
    5. cholesterol: Serum cholesterol (mg/dl)
    6. fasting_bs: Fasting blood sugar > 120 mg/dl (1=True, 0=False)
    7. resting_ecg: Resting ECG results (0-2)
    8. max_heart_rate: Maximum heart rate achieved
    9. exercise_angina: Exercise induced angina (1=Yes, 0=No)
    10. oldpeak: ST depression induced by exercise
    11. st_slope: Slope of peak exercise ST segment (0-2)
    
    GOVERNANCE FIELDS:
    - doctor: Who recorded the data
    - hospital: Which hospital's patient (for FL partitioning)
    - created_at: When data was recorded
    """
    
    # Clinical Features
    age = IntField(required=True, min_value=1, max_value=120)
    sex = IntField(required=True, min_value=0, max_value=1)  # 0=Female, 1=Male
    chest_pain_type = IntField(required=True, min_value=0, max_value=3)
    resting_bp = IntField(required=True, min_value=0)
    cholesterol = IntField(required=True, min_value=0)
    fasting_bs = IntField(required=True, min_value=0, max_value=1)
    resting_ecg = IntField(required=True, min_value=0, max_value=2)
    max_heart_rate = IntField(required=True, min_value=0, max_value=220)
    exercise_angina = IntField(required=True, min_value=0, max_value=1)
    oldpeak = FloatField(required=True)
    st_slope = IntField(required=True, min_value=0, max_value=2)
    
    # Governance & Traceability
    doctor = ReferenceField('hospitals.Doctor', required=True)
    hospital = ReferenceField('hospitals.Hospital', required=True)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'patient_data',
        'indexes': [
            'doctor',
            'hospital',
            '-created_at',
            {'fields': ['hospital', '-created_at']},  # Hospital-wise recent patients
        ]
    }
    
    def __str__(self):
        return f"Patient {self.id} - Age {self.age}"
    
    def to_feature_vector(self):
        """
        Convert patient data to feature vector for ML model.
        
        Returns:
            list: [age, sex, cp, bp, chol, fbs, ecg, hr, ea, oldpeak, slope]
        """
        return [
            self.age,
            self.sex,
            self.chest_pain_type,
            self.resting_bp,
            self.cholesterol,
            self.fasting_bs,
            self.resting_ecg,
            self.max_heart_rate,
            self.exercise_angina,
            self.oldpeak,
            self.st_slope
        ]


class PredictionResult(Document):
    """
    ML model prediction results for patient data.
    
    STORES:
    - prediction: Binary classification (0=Low Risk, 1=High Risk)
    - probability: Model confidence (0.0 to 1.0)
    - confidence_score: Percentage confidence
    - model_version: Which model was used (for FL tracking)
    
    WHY SEPARATE FROM PATIENT DATA:
    - One patient can have multiple predictions over time
    - Allows comparing predictions from different models
    - Tracks model evolution in FL (global vs local models)
    """
    
    # Reference to patient data
    patient = ReferenceField(PatientData, required=True)
    
    # Prediction Results
    prediction = IntField(required=True, min_value=0, max_value=1)  # 0=Low Risk, 1=High Risk
    prediction_label = StringField(required=True)  # "Low Risk" or "High Risk"
    probability = FloatField(required=True, min_value=0.0, max_value=1.0)
    confidence_score = FloatField(required=True)  # Percentage (0-100)
    
    # Model Tracking (for FL)
    model_version = StringField(default='v1.0')
    model_type = StringField(default='RandomForest')  # Can be Global or Local model
    
    # Governance
    doctor = ReferenceField('hospitals.Doctor', required=True)
    hospital = ReferenceField('hospitals.Hospital', required=True)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'prediction_results',
        'indexes': [
            'patient',
            'doctor',
            'hospital',
            '-created_at',
            {'fields': ['hospital', '-created_at']},
            {'fields': ['doctor', '-created_at']},
        ],
        'ordering': ['-created_at']
    }
    
    def __str__(self):
        return f"{self.prediction_label} ({self.confidence_score:.1f}%)"
    
    @property
    def risk_level(self):
        """Get human-readable risk level"""
        return "High Risk" if self.prediction == 1 else "Low Risk"
