"""
MongoDB Document Models for Core App
=====================================

Uses MongoEngine to define document schemas for contact messages.

WHY MONGODB FOR CONTACT MESSAGES:
- Flexible schema allows adding custom fields later
- Easy to export and analyze user feedback
- No need for migrations when adding new fields
"""

from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField
from datetime import datetime


class ContactMessage(Document):
    """
    Contact form submissions from users.
    
    SCHEMA DESIGN:
    - name: User's full name
    - email: Contact email (validated format)
    - phone: Contact phone number (optional)
    - subject: Message topic
    - message: Actual message content
    - is_read: Admin tracking flag
    - created_at: Automatic timestamp
    
    INDEXES:
    - created_at: For chronological listing
    - is_read: For filtering unread messages
    """
    
    name = StringField(required=True, max_length=100)
    email = EmailField(required=True)
    phone = StringField(max_length=20)  # Optional phone field
    subject = StringField(required=True, max_length=200)
    message = StringField(required=True)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'contact_messages',
        'indexes': [
            '-created_at',  # Descending index for recent-first queries
            'is_read',      # For filtering unread messages
        ],
        'ordering': ['-created_at']
    }
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    def mark_as_read(self):
        """Mark this message as read by admin"""
        self.is_read = True
        self.save()
