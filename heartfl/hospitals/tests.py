# Hospitals App Tests
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Hospital, Doctor


class HospitalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='hospital1',
            email='hospital@test.com',
            password='testpass123'
        )
    
    def test_hospital_creation(self):
        """Test hospital creation"""
        hospital = Hospital.objects.create(
            user=self.user,
            name='Test Hospital',
            address='123 Test St',
            city='Test City',
            state='Test State',
            pincode='123456',
            contact_number='+91 1234567890',
            email='hospital@test.com',
            registration_number='REG-TEST-001'
        )
        self.assertEqual(hospital.name, 'Test Hospital')
        self.assertFalse(hospital.is_verified)
