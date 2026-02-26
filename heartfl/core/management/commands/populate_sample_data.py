"""
Django management command to populate database with sample data.

Usage:
    python manage.py populate_sample_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from hospitals.models import Hospital, Doctor, HospitalDataset
from prediction.models import PatientData, PredictionResult
from federated.models import FederatedRound, LocalModel
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = "Populate the database with sample data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()

        self.create_hospitals()
        self.create_doctors()
        self.create_patient_data()
        self.create_predictions()
        self.create_federated_rounds()

        self.stdout.write(
            self.style.SUCCESS('\n✅ Sample data successfully created!')
        )

    def clear_data(self):
        """Clear all data"""
        self.stdout.write(self.style.WARNING('\n🗑️  Clearing all data...'))
        User.objects.all().delete()
        Hospital.objects.all().delete()
        Doctor.objects.all().delete()
        PatientData.objects.all().delete()
        PredictionResult.objects.all().delete()
        HospitalDataset.objects.all().delete()
        FederatedRound.objects.all().delete()
        LocalModel.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ All data cleared'))

    def create_hospitals(self):
        """Create 3 sample hospitals"""
        self.stdout.write(self.style.SUCCESS('\n=== Creating Hospitals ==='))

        hospitals_data = [
            {
                'username': 'apollo_mumbai',
                'email': 'apollo@example.com',
                'password': 'Hospital@123',
                'name': 'Apollo Hospital Mumbai',
                'reg_num': 'MH-HOSP-2024-001',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'pincode': '400001',
                'address': '123 Marine Drive, Mumbai',
                'phone': '+91 9876543210'
            },
            {
                'username': 'aiims_delhi',
                'email': 'aiims@example.com',
                'password': 'Hospital@123',
                'name': 'AIIMS Delhi',
                'reg_num': 'DL-HOSP-2024-001',
                'city': 'New Delhi',
                'state': 'Delhi',
                'pincode': '110029',
                'address': 'Ansari Nagar, New Delhi',
                'phone': '+91 9876543211'
            },
            {
                'username': 'fortis_bangalore',
                'email': 'fortis@example.com',
                'password': 'Hospital@123',
                'name': 'Fortis Hospital Bangalore',
                'reg_num': 'KA-HOSP-2024-001',
                'city': 'Bangalore',
                'state': 'Karnataka',
                'pincode': '560001',
                'address': 'MG Road, Bangalore',
                'phone': '+91 9876543212'
            }
        ]

        for data in hospitals_data:
            # Create Django User if not exists
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['name'].split()[0],
                    'last_name': ' '.join(data['name'].split()[1:]),
                }
            )
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(f"✓ Created user: {user.username}")
            else:
                self.stdout.write(f"✓ User already exists: {user.username}")

            # Create UserProfile if not exists
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'user_type': 'hospital',
                    'phone': data['phone']
                }
            )
            if created:
                self.stdout.write(f"✓ Created profile for: {user.username}")

            # Create Hospital if not exists
            hospital, created = Hospital.objects.get_or_create(
                user=user,
                defaults={
                    'name': data['name'],
                    'address': data['address'],
                    'city': data['city'],
                    'state': data['state'],
                    'pincode': data['pincode'],
                    'contact_number': data['phone'],
                    'email': data['email'],
                    'registration_number': data['reg_num'],
                    'is_verified': True
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created hospital: {hospital.name}")
                )

    def create_doctors(self):
        """Create doctors for each hospital"""
        self.stdout.write(self.style.SUCCESS('\n=== Creating Doctors ==='))

        hospitals = Hospital.objects.all()

        doctors_per_hospital = [
            {
                'username': 'dr_kumar',
                'email': 'dr.kumar@example.com',
                'password': 'Doctor@123',
                'full_name': 'Dr. Rajesh Kumar',
                'specialization': 'Cardiology',
                'license': 'MCI-2024-001'
            },
            {
                'username': 'dr_sharma',
                'email': 'dr.sharma@example.com',
                'password': 'Doctor@123',
                'full_name': 'Dr. Priya Sharma',
                'specialization': 'Internal Medicine',
                'license': 'MCI-2024-002'
            },
            {
                'username': 'dr_patel',
                'email': 'dr.patel@example.com',
                'password': 'Doctor@123',
                'full_name': 'Dr. Amit Patel',
                'specialization': 'General Medicine',
                'license': 'MCI-2024-003'
            },
        ]

        for hospital in hospitals:
            for idx, doc_data in enumerate(doctors_per_hospital):
                username = f"{doc_data['username']}_{hospital.id}"
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': doc_data['email'],
                        'first_name': doc_data['full_name'].split()[1],
                        'last_name': doc_data['full_name'].split()[2],
                    }
                )
                if created:
                    user.set_password(doc_data['password'])
                    user.save()
                    self.stdout.write(f"✓ Created user: {user.username}")

                # Create UserProfile
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'user_type': 'doctor',
                        'phone': f'+91 988000{idx:04d}'
                    }
                )

                # Create Doctor
                doctor, created = Doctor.objects.get_or_create(
                    user=user,
                    defaults={
                        'hospital': hospital,
                        'full_name': doc_data['full_name'],
                        'specialization': doc_data['specialization'],
                        'license_number': f"{doc_data['license']}_{hospital.id}",
                        'phone': f'+91 988000{idx:04d}',
                        'email': doc_data['email'],
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Created doctor: {doctor.full_name} at {hospital.name}"
                        )
                    )

    def create_patient_data(self):
        """Create sample patient records"""
        self.stdout.write(self.style.SUCCESS('\n=== Creating Patient Records ==='))

        doctors = Doctor.objects.all()

        patient_names = [
            'Rajesh Singh', 'Anjali Verma', 'Arjun Nair', 'Neha Kapoor',
            'Vikram Reddy', 'Priya Gupta', 'Rohan Desai', 'Divya Kumar'
        ]

        for doctor in doctors:
            for i, name in enumerate(patient_names[:3]):  # 3 patients per doctor
                patient, created = PatientData.objects.get_or_create(
                    doctor=doctor,
                    patient_name=name,
                    age=random.randint(30, 75),
                    defaults={
                        'gender': random.choice(['M', 'F']),
                        'chest_pain_type': random.randint(0, 3),
                        'resting_bp': random.randint(90, 180),
                        'cholesterol': random.randint(120, 400),
                        'fasting_bs': random.choice([True, False]),
                        'resting_ecg': random.randint(0, 2),
                        'max_heart_rate': random.randint(60, 200),
                        'exercise_angina': random.choice([True, False]),
                        'oldpeak': round(random.uniform(0, 6.2), 1),
                        'st_slope': random.randint(0, 2),
                    }
                )
                if created:
                    self.stdout.write(
                        f"✓ Created patient: {name} for Dr. {doctor.full_name}"
                    )

    def create_predictions(self):
        """Create sample prediction results"""
        self.stdout.write(self.style.SUCCESS('\n=== Creating Predictions ==='))

        patients = PatientData.objects.all()

        for patient in patients:
            # Create 1-3 predictions per patient
            for i in range(random.randint(1, 3)):
                prediction = random.choice(['high', 'low'])
                probability = random.uniform(50, 99) if prediction == 'high' else random.uniform(10, 49)

                pred_result, created = PredictionResult.objects.get_or_create(
                    patient_data=patient,
                    doctor=patient.doctor,
                    defaults={
                        'prediction': prediction,
                        'probability': round(probability, 2),
                        'confidence_score': round(random.uniform(0.7, 0.99), 2) * 100,
                        'model_version': 'v1.0',
                        'notes': f'Patient presents with {["typical", "atypical"][random.randint(0, 1)]} symptoms. Further evaluation recommended.' if prediction == 'high' else 'Patient in good health. Regular checkup recommended.'
                    }
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Created prediction: {patient.patient_name} - {prediction.upper()}"
                        )
                    )

    def create_federated_rounds(self):
        """Create sample federated learning rounds"""
        self.stdout.write(self.style.SUCCESS('\n=== Creating Federated Learning Rounds ==='))

        hospitals = Hospital.objects.all()

        for round_num in range(1, 4):  # 3 rounds
            fl_round, created = FederatedRound.objects.get_or_create(
                round_number=round_num,
                defaults={
                    'status': 'completed' if round_num < 3 else 'in_progress',
                    'global_accuracy': round(0.85 + (round_num * 0.02), 4),
                    'total_samples': random.randint(1000, 5000),
                    'started_at': datetime.now() - timedelta(days=7 * (3 - round_num)),
                    'completed_at': datetime.now() - timedelta(days=7 * (3 - round_num) - 2) if round_num < 3 else None
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created FL Round {fl_round.round_number}")
                )

                # Create local models for each hospital
                for hospital in hospitals:
                    local_model, created = LocalModel.objects.get_or_create(
                        federated_round=fl_round,
                        hospital=hospital,
                        defaults={
                            'accuracy': round(0.80 + (round_num * 0.02), 4),
                            'samples_used': random.randint(100, 500),
                            'parameters_sent': random.randint(1000000, 5000000),
                            'training_time_seconds': random.randint(30, 300)
                        }
                    )
                    if created:
                        self.stdout.write(
                            f"  ✓ Created local model for {hospital.name}"
                        )
