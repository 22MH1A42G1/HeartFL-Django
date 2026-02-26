"""
MongoDB Document Models for Accounts App
=========================================

Extends Django's built-in User model with additional profile data.

HYBRID AUTHENTICATION APPROACH:
- Django User model (SQLite): Handles authentication, sessions, admin
- UserProfile document (MongoDB): Stores extended user metadata
- Linked by username field

WHY THIS DESIGN:
- Django admin panel works out-of-the-box
- Leverages Django's battle-tested authentication
- MongoDB stores application-specific user data
- Easy to explain in viva: "Best of both worlds"
"""

from mongoengine import (
    Document, StringField, EmailField, BooleanField,
    DateTimeField, ReferenceField
)
from datetime import datetime


class UserProfile(Document):
    """
    Extended user profile stored in MongoDB.
    Linked to Django User model by username.
    
    USER TYPES:
    - hospital: Can upload datasets, view FL dashboard
    - doctor: Can make predictions, view history
    
    LINKAGE:
    - username matches Django User.username
    - When user logs in via Django auth, we fetch this profile
    - Profile determines permissions and dashboard access
    """
    
    # Link to Django User (by username)
    username = StringField(required=True, unique=True, max_length=150)
    email = EmailField(required=True)
    
    # User Type (determines permissions)
    user_type = StringField(
        required=True,
        choices=['hospital', 'doctor'],
    )
    
    # Contact Info
    phone = StringField(max_length=20)
    
    # Profile Status
    is_active = BooleanField(default=True)
    email_verified = BooleanField(default=False)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()
    
    meta = {
        'collection': 'user_profiles',
        'indexes': [
            'username',
            'email',
            'user_type',
        ]
    }
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"
    
    def is_hospital(self):
        """Check if user is hospital"""
        return self.user_type == 'hospital'
    
    def is_doctor(self):
        """Check if user is doctor"""
        return self.user_type == 'doctor'
    
    def get_related_document(self):
        """
        Get the related Hospital or Doctor document.
        
        Returns:
            Hospital or Doctor document based on user_type
        """
        if self.is_hospital():
            from hospitals.documents import Hospital
            return Hospital.objects(username=self.username).first()
        elif self.is_doctor():
            from hospitals.documents import Doctor
            return Doctor.objects(username=self.username).first()
        return None
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.save()
