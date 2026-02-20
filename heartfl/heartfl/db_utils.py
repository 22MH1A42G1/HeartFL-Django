"""
Database Utilities for MongoDB Operations
==========================================

Helper functions for common database queries and operations.
"""
from hospitals.documents import Hospital, Doctor, HospitalDataset
from prediction.documents import PatientData, PredictionResult
from federated.documents import FederatedRound, LocalModel
from accounts.documents import UserProfile


def get_hospital_stats(hospital):
    """
    Get statistics for a hospital.
    
    Args:
        hospital: Hospital document
    
    Returns:
        dict: Statistics including doctor count, patient count, predictions
    """
    return {
        'hospital_name': hospital.name,
        'doctor_count': Doctor.objects(hospital=hospital).count(),
        'patient_count': PatientData.objects(hospital=hospital).count(),
        'prediction_count': PredictionResult.objects(hospital=hospital).count(),
        'high_risk_count': PredictionResult.objects(hospital=hospital, prediction=1).count(),
        'low_risk_count': PredictionResult.objects(hospital=hospital, prediction=0).count(),
        'dataset_count': HospitalDataset.objects(hospital=hospital).count(),
    }


def get_doctor_stats(doctor):
    """
    Get statistics for a doctor.
    
    Args:
        doctor: Doctor document
    
    Returns:
        dict: Statistics including patient count, predictions
    """
    return {
        'doctor_name': doctor.name,
        'hospital_name': doctor.hospital.name,
        'patient_count': PatientData.objects(doctor=doctor).count(),
        'prediction_count': PredictionResult.objects(doctor=doctor).count(),
        'high_risk_count': PredictionResult.objects(doctor=doctor, prediction=1).count(),
        'low_risk_count': PredictionResult.objects(doctor=doctor, prediction=0).count(),
    }


def get_fl_dashboard_stats():
    """
    Get federated learning dashboard statistics.
    
    Returns:
        dict: FL statistics including active hospitals, rounds, accuracy
    """
    active_hospitals = Hospital.objects(is_active=True, is_verified=True)
    latest_round = FederatedRound.objects().order_by('-round_number').first()
    
    # Get unique hospitals with datasets
    hospitals_with_datasets = len(HospitalDataset.objects(is_available_for_fl=True).distinct('hospital'))
    
    stats = {
        'total_hospitals': Hospital.objects().count(),
        'active_hospitals': active_hospitals.count(),
        'total_doctors': Doctor.objects().count(),
        'total_patients': PatientData.objects().count(),
        'total_predictions': PredictionResult.objects().count(),
        'fl_rounds': FederatedRound.objects().count(),
        'latest_round': latest_round,
        'hospitals_with_datasets': hospitals_with_datasets,
    }
    
    if latest_round:
        stats['latest_accuracy'] = latest_round.global_accuracy
        stats['latest_status'] = latest_round.status
    
    return stats


def get_recent_predictions(limit=10, hospital=None, doctor=None):
    """
    Get recent predictions with filters.
    
    Args:
        limit: Number of predictions to return
        hospital: Filter by hospital (optional)
        doctor: Filter by doctor (optional)
    
    Returns:
        QuerySet: Recent predictions
    """
    query = {}
    
    if hospital:
        query['hospital'] = hospital
    
    if doctor:
        query['doctor'] = doctor
    
    return PredictionResult.objects(**query).order_by('-created_at')[:limit]


def get_hospital_by_username(username):
    """
    Get hospital document by Django username.
    
    Args:
        username: Django User username
    
    Returns:
        Hospital document or None
    """
    return Hospital.objects(username=username).first()


def get_doctor_by_username(username):
    """
    Get doctor document by Django username.
    
    Args:
        username: Django User username
    
    Returns:
        Doctor document or None
    """
    return Doctor.objects(username=username).first()


def get_user_profile(username):
    """
    Get user profile from MongoDB.
    
    Args:
        username: Django User username
    
    Returns:
        UserProfile document or None
    """
    return UserProfile.objects(username=username).first()


def hospital_can_participate_in_fl(hospital):
    """
    Check if hospital can participate in federated learning.
    
    Requirements:
    - Hospital must be verified
    - Hospital must be active
    - Hospital must have at least one dataset uploaded
    
    Args:
        hospital: Hospital document
    
    Returns:
        (bool, str): (can_participate, reason)
    """
    if not hospital.is_verified:
        return False, "Hospital not verified"
    
    if not hospital.is_active:
        return False, "Hospital not active"
    
    dataset_count = HospitalDataset.objects(hospital=hospital, is_available_for_fl=True).count()
    if dataset_count == 0:
        return False, "No datasets available for FL"
    
    return True, "Hospital can participate"


def get_all_fl_participants():
    """
    Get all hospitals that can participate in federated learning.
    
    Returns:
        QuerySet: Eligible hospitals
    """
    return Hospital.objects(
        is_verified=True,
        is_active=True
    )


def cleanup_test_data():
    """
    Remove all test data from MongoDB.
    WARNING: Use only for development/testing!
    """
    print("⚠️  Cleaning up all data from MongoDB...")
    
    # Delete in correct order (respecting references)
    PredictionResult.objects().delete()
    print("  ✓ Deleted prediction results")
    
    PatientData.objects().delete()
    print("  ✓ Deleted patient data")
    
    LocalModel.objects().delete()
    print("  ✓ Deleted local models")
    
    FederatedRound.objects().delete()
    print("  ✓ Deleted FL rounds")
    
    HospitalDataset.objects().delete()
    print("  ✓ Deleted hospital datasets")
    
    Doctor.objects().delete()
    print("  ✓ Deleted doctors")
    
    Hospital.objects().delete()
    print("  ✓ Deleted hospitals")
    
    UserProfile.objects().delete()
    print("  ✓ Deleted user profiles")
    
    print("✅ Cleanup complete!")


def export_hospital_data_to_csv(hospital, output_path):
    """
    Export hospital's patient data to CSV.
    
    Args:
        hospital: Hospital document
        output_path: Path to save CSV file
    """
    import csv
    
    patients = PatientData.objects(hospital=hospital)
    
    with open(output_path, 'w', newline='') as csvfile:
        fieldnames = [
            'age', 'sex', 'chest_pain_type', 'resting_bp', 'cholesterol',
            'fasting_bs', 'resting_ecg', 'max_heart_rate', 'exercise_angina',
            'oldpeak', 'st_slope', 'doctor', 'created_at'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for patient in patients:
            writer.writerow({
                'age': patient.age,
                'sex': patient.sex,
                'chest_pain_type': patient.chest_pain_type,
                'resting_bp': patient.resting_bp,
                'cholesterol': patient.cholesterol,
                'fasting_bs': patient.fasting_bs,
                'resting_ecg': patient.resting_ecg,
                'max_heart_rate': patient.max_heart_rate,
                'exercise_angina': patient.exercise_angina,
                'oldpeak': patient.oldpeak,
                'st_slope': patient.st_slope,
                'doctor': patient.doctor.name,
                'created_at': patient.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    print(f"✓ Exported {patients.count()} patient records to {output_path}")
