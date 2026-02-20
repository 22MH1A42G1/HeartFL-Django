"""
ML Model Integration
Heart Disease Prediction using scikit-learn
This module handles loading and using the pre-trained model
"""
import os
import pickle
import numpy as np
from django.conf import settings


class HeartDiseasePredictor:
    """
    Heart Disease Prediction Model Wrapper
    Loads the pre-trained model and makes predictions
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.model_path = os.path.join(settings.BASE_DIR, 'ml_models', 'heart_disease_model.pkl')
        self.scaler_path = os.path.join(settings.BASE_DIR, 'ml_models', 'scaler.pkl')
        self.load_model()
    
    def load_model(self):
        """
        Load the pre-trained model and scaler from pickle files
        If model doesn't exist, use a dummy predictor for demo
        """
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print("Heart disease model loaded successfully")
            else:
                print("Model file not found. Using dummy predictor for demo.")
                self.model = None
            
            # Load scaler if available
            if os.path.exists(self.scaler_path):
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                print("Feature scaler loaded successfully")
            else:
                self.scaler = None
        except Exception as e:
            print(f"Error loading model: {e}. Using dummy predictor.")
            self.model = None
            self.scaler = None
    
    def predict_from_features(self, features_list):
        """
        Make prediction from feature vector (list of 11 values).
        
        Args:
            features_list: List of 11 features [age, sex, cp, bp, chol, fbs, ecg, hr, ea, oldpeak, slope]
        
        Returns:
            (prediction_label, probability_percentage)
        """
        features = np.array(features_list, dtype=float).reshape(1, -1)
        
        if self.model is not None:
            try:
                # Keep inference preprocessing aligned with training.
                if self.scaler is not None:
                    features = self.scaler.transform(features)

                prediction = self.model.predict(features)[0]
                probability = self.model.predict_proba(features)[0]
                
                # Get probability for positive class (heart disease)
                prob_percentage = probability[1] * 100
                
                result = 'High Risk' if prediction == 1 else 'Low Risk'
                return result, float(prob_percentage)
                
            except Exception as e:
                print(f"Prediction error: {e}")
                return self._dummy_prediction_from_features(features_list)
        else:
            return self._dummy_prediction_from_features(features_list)
    
    def _dummy_prediction_from_features(self, features_list):
        """
        Dummy predictor using feature vector (for backward compatibility).
        Uses comprehensive risk scoring based on established factors.
        """
        # features_list: [age, sex, cp, bp, chol, fbs, ecg, hr, ea, oldpeak, slope]
        age = features_list[0]
        sex = features_list[1]  # 1=Male, 0=Female
        chest_pain_type = features_list[2]
        resting_bp = features_list[3]
        cholesterol = features_list[4]
        fasting_bs = features_list[5]
        resting_ecg = features_list[6]
        max_heart_rate = features_list[7]
        exercise_angina = features_list[8]
        oldpeak = features_list[9]
        st_slope = features_list[10]
        
        risk_score = 20  # Base score
        
        # Age risk
        if age >= 70:
            risk_score += 25
        elif age >= 60:
            risk_score += 20
        elif age >= 50:
            risk_score += 15
        elif age >= 40:
            risk_score += 8
        else:
            risk_score += 2
        
        # Sex risk
        if sex == 1:
            risk_score += 10
        
        # Cholesterol risk
        if cholesterol >= 300:
            risk_score += 30
        elif cholesterol >= 240:
            risk_score += 25
        elif cholesterol >= 200:
            risk_score += 15
        elif cholesterol >= 160:
            risk_score += 5
        elif cholesterol < 160:
            risk_score -= 2
        
        # Blood Pressure risk
        if resting_bp >= 180:
            risk_score += 25
        elif resting_bp >= 160:
            risk_score += 20
        elif resting_bp >= 140:
            risk_score += 15
        elif resting_bp >= 130:
            risk_score += 10
        elif resting_bp >= 120:
            risk_score += 5
        elif resting_bp < 120:
            risk_score -= 3
        
        # Heart Rate risk
        if max_heart_rate < 60:
            risk_score += 15
        elif max_heart_rate < 70:
            risk_score += 8
        elif max_heart_rate <= 100:
            risk_score -= 2
        elif max_heart_rate <= 120:
            risk_score += 3
        elif max_heart_rate <= 150:
            risk_score += 8
        else:
            risk_score += 12
        
        # Chest Pain Type risk
        if chest_pain_type == 0:
            risk_score += 20
        elif chest_pain_type == 1:
            risk_score += 12
        elif chest_pain_type == 2:
            risk_score += 5
        else:
            risk_score += 2
        
        # Exercise-induced Angina risk
        if exercise_angina == 1:
            risk_score += 25
        
        # ST Depression risk
        if oldpeak >= 3.0:
            risk_score += 30
        elif oldpeak >= 2.0:
            risk_score += 25
        elif oldpeak >= 1.5:
            risk_score += 20
        elif oldpeak >= 1.0:
            risk_score += 15
        elif oldpeak >= 0.5:
            risk_score += 10
        elif oldpeak > 0:
            risk_score += 5
        
        # ST Slope risk
        if st_slope == 2:
            risk_score += 15
        elif st_slope == 1:
            risk_score += 8
        
        # Resting ECG risk
        if resting_ecg == 2:
            risk_score += 15
        elif resting_ecg == 1:
            risk_score += 10
        
        # Fasting Blood Sugar risk
        if fasting_bs == 1:
            risk_score += 15
        
        # Normalize score
        risk_score = max(10, min(95, risk_score))
        
        # High risk if >= 50
        result = 'High Risk' if risk_score >= 50 else 'Low Risk'
        probability = risk_score
        
        return result, probability
    
    def prepare_features(self, patient_data):
        """
        Prepare patient data for prediction
        Convert model fields to feature array
        """
        features = [
            patient_data.age,
            1 if patient_data.gender == 'M' else 0,  # Sex: 1=Male, 0=Female
            patient_data.chest_pain_type,
            patient_data.resting_bp,
            patient_data.cholesterol,
            1 if patient_data.fasting_bs else 0,
            patient_data.resting_ecg,
            patient_data.max_heart_rate,
            1 if patient_data.exercise_angina else 0,
            patient_data.oldpeak,
            patient_data.st_slope
        ]
        return np.array(features).reshape(1, -1)
    
    def predict(self, patient_data):
        """
        Make prediction for patient data
        Returns: (prediction_label, probability_percentage)
        """
        features = self.prepare_features(patient_data)
        
        if self.model is not None:
            try:
                # Scale features if scaler available
                if self.scaler is not None:
                    features_scaled = self.scaler.transform(features)
                else:
                    features_scaled = features
                
                # Use actual model prediction
                prediction = self.model.predict(features_scaled)[0]
                probability = self.model.predict_proba(features_scaled)[0]
                
                # Get probability for positive class (heart disease)
                prob_percentage = probability[1] * 100
                
                result = 'high' if prediction == 1 else 'low'
                return result, float(prob_percentage)
                
            except Exception as e:
                print(f"Prediction error: {e}")
                return self._dummy_prediction(features)
        else:
            # Use dummy prediction for demo
            return self._dummy_prediction(features)
    
    def _dummy_prediction(self, features):
        """
        Improved dummy prediction logic using comprehensive risk scoring.
        Based on established cardiovascular risk factors.
        
        Features: [age, sex(1=M,0=F), chest_pain, bp, cholesterol, fasting_bs, ecg, hr, exercise_angina, oldpeak, st_slope]
        """
        # Extract all features
        age = features[0][0]
        sex = features[0][1]  # 1=Male, 0=Female
        chest_pain_type = features[0][2]
        resting_bp = features[0][3]
        cholesterol = features[0][4]
        fasting_bs = features[0][5]  # 1=True(>120), 0=False
        resting_ecg = features[0][6]
        max_heart_rate = features[0][7]
        exercise_angina = features[0][8]  # 1=Yes, 0=No
        oldpeak = features[0][9]  # ST depression
        st_slope = features[0][10]
        
        risk_score = 20  # Base score
        
        # ============ AGE RISK (important predictor) ============
        if age >= 70:
            risk_score += 25
        elif age >= 60:
            risk_score += 20
        elif age >= 50:
            risk_score += 15
        elif age >= 40:
            risk_score += 8
        else:
            risk_score += 2  # Even young people can have risk
        
        # ============ SEX RISK ============
        # Males have higher risk, but females with risk factors also at risk
        if sex == 1:  # Male
            risk_score += 10
        
        # ============ CHOLESTEROL RISK (strong predictor) ============
        if cholesterol >= 300:
            risk_score += 30
        elif cholesterol >= 240:
            risk_score += 25
        elif cholesterol >= 200:
            risk_score += 15
        elif cholesterol >= 160:
            risk_score += 5
        # Low cholesterol is protective
        elif cholesterol < 160:
            risk_score -= 2
        
        # ============ BLOOD PRESSURE RISK (strong predictor) ============
        if resting_bp >= 180:
            risk_score += 25
        elif resting_bp >= 160:
            risk_score += 20
        elif resting_bp >= 140:
            risk_score += 15
        elif resting_bp >= 130:
            risk_score += 10
        elif resting_bp >= 120:
            risk_score += 5
        # Normal BP is protective
        elif resting_bp < 120:
            risk_score -= 3
        
        # ============ HEART RATE RISK ============
        # Both too low (<60) and too high (>100) are concerning
        if max_heart_rate < 60:
            risk_score += 15  # Low HR can indicate cardiac issues
        elif max_heart_rate < 70:
            risk_score += 8
        elif max_heart_rate <= 100:
            risk_score -= 2  # Normal resting HR is good
        elif max_heart_rate <= 120:
            risk_score += 3  # Slightly elevated
        elif max_heart_rate <= 150:
            risk_score += 8  # Elevated
        else:  # >150
            risk_score += 12  # High HR concerning
        
        # ============ CHEST PAIN TYPE RISK ============
        # 0=Typical Angina, 1=Atypical, 2=Non-anginal, 3=Asymptomatic
        if chest_pain_type == 0:
            risk_score += 20  # Typical angina is concerning
        elif chest_pain_type == 1:
            risk_score += 12  # Atypical is moderate
        elif chest_pain_type == 2:
            risk_score += 5   # Non-anginal is mild
        else:
            risk_score += 2   # Asymptomatic (but needs context)
        
        # ============ EXERCISE-INDUCED ANGINA RISK (strong predictor) ============
        if exercise_angina == 1:
            risk_score += 25  # Very concerning indicator
        
        # ============ ST DEPRESSION (OLDPEAK) RISK (strong predictor) ============
        if oldpeak >= 3.0:
            risk_score += 30  # Severe ST depression
        elif oldpeak >= 2.0:
            risk_score += 25
        elif oldpeak >= 1.5:
            risk_score += 20
        elif oldpeak >= 1.0:
            risk_score += 15
        elif oldpeak >= 0.5:
            risk_score += 10
        elif oldpeak > 0:
            risk_score += 5
        
        # ============ ST SLOPE RISK ============
        # 0=Upsloping (good), 1=Flat (moderate), 2=Downsloping (bad)
        if st_slope == 2:
            risk_score += 15  # Downsloping is concerning
        elif st_slope == 1:
            risk_score += 8   # Flat is moderate
        # Upsloping is neutral (0)
        
        # ============ RESTING ECG RISK ============
        # 0=Normal, 1=ST-T wave abnormality, 2=LVH
        if resting_ecg == 2:
            risk_score += 15  # Left ventricular hypertrophy
        elif resting_ecg == 1:
            risk_score += 10  # ST-T wave abnormality
        
        # ============ FASTING BLOOD SUGAR RISK (diabetes) ============
        if fasting_bs == 1:  # >120 mg/dl
            risk_score += 15  # Diabetes/high blood sugar is risk factor
        
        # ============ NORMALIZE SCORE ============
        # Clamp between 10-95 (never 0 or 100 for realism)
        risk_score = max(10, min(95, risk_score))
        
        # ============ DETERMINE PREDICTION ============
        # Using 50th percentile as threshold
        # High risk: >= 50, Low risk: < 50
        prediction = 'high' if risk_score >= 50 else 'low'
        
        return prediction, float(risk_score)


