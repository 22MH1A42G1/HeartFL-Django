# Core App Tests
from django.test import TestCase
from django.contrib.auth.models import User
from .models import ContactMessage


class ContactMessageTest(TestCase):
    def test_contact_message_creation(self):
        """Test contact message can be created"""
        message = ContactMessage.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Subject",
            message="Test message cont"
        )
        self.assertEqual(message.name, "Test User")
        self.assertFalse(message.is_read)

