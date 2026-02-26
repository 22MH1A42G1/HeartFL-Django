# Accounts App Tests
from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test user profile creation"""
        profile = UserProfile.objects.create(
            user=self.user,
            user_type='hospital',
            phone='+91 1234567890'
        )
        self.assertEqual(profile.user_type, 'hospital')
        self.assertTrue(profile.is_hospital())
        self.assertFalse(profile.is_doctor())
