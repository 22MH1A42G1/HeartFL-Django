"""
MongoDB Document Models for Hospitals App
==========================================

SCHEMA DESIGN RATIONALE:
- Hospital: Central entity in federated learning system
- Doctor: Must reference an existing hospital (enforced at document level)
- HospitalDataset: Metadata about uploaded CSV files for FL training

WHY THIS DESIGN SUPPORTS FEDERATED LEARNING:
1. Each hospital is an independent node in the FL network
2. Datasets are stored as metadata (not raw data) for privacy
3. Doctor-Hospital linkage ensures data governance
4. Timestamps track when nodes join the network
5. Active status enables dynamic node management
"""

from mongoengine import (
    Document, StringField, EmailField, BooleanField, 
    DateTimeField, ReferenceField, IntField, FileField,
    ValidationError
)
from datetime import datetime
from django.contrib.auth.models import User


class Hospital(Document):
    """
    Hospital entity - represents a federated learning node.
    
    CRITICAL FIELDS FOR FL:
    - registration_number: Unique hospital identifier
    - is_verified: Only verified hospitals can participate in FL
    - is_active: Enables/disables hospital from FL rounds
    - registration_date: Tracks when hospital joined network
    
    DATA PRIVACY:
    - Stores only metadata, not patient data
    - Each hospital's data stays local in their CSV files
    """
    
    # Link to Django User (for authentication)
    username = StringField(required=True, unique=True, max_length=150)
    email = EmailField(required=True, unique=True)
    
    # Hospital Details
    name = StringField(required=True, max_length=200)
    registration_number = StringField(required=True, unique=True, max_length=100)
    
    # Location
    address = StringField(required=True, max_length=300)
    city = StringField(required=True, max_length=100)
    state = StringField(required=True, max_length=100)
    pincode = StringField(required=True, max_length=10)
    
    # Contact
    contact_number = StringField(required=True, max_length=20)
    
    # Status Tracking
    is_verified = BooleanField(default=False)
    is_active = BooleanField(default=True)
    registration_date = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'hospitals',
        'indexes': [
            'registration_number',
            'username',
            'email',
            {'fields': ['is_verified', 'is_active']},  # Compound index for FL queries
        ]
    }
    
    def __str__(self):
        return f"{self.name} ({self.registration_number})"
    
    def get_dataset_count(self):
        """Get number of datasets uploaded by this hospital"""
        return HospitalDataset.objects(hospital=self).count()
    
    def get_doctor_count(self):
        """Get number of doctors associated with this hospital"""
        return Doctor.objects(hospital=self).count()


class Doctor(Document):
    """
    Doctor entity - can only register if hospital exists.
    
    IMPORTANT VALIDATION:
    - Must reference an existing Hospital document
    - Enforces FK-like constraint at application level
    
    WHY DOCTORS NEED HOSPITAL LINKAGE:
    - Predictions are traced back to hospitals for FL
    - Data governance: know which hospital's doctor made prediction
    - Privacy: predictions stay within hospital's data domain
    """
    
    # Link to Django User (for authentication)
    username = StringField(required=True, unique=True, max_length=150)
    email = EmailField(required=True, unique=True)
    
    # Doctor Details
    name = StringField(required=True, max_length=200)
    specialization = StringField(max_length=100)
    license_number = StringField(required=True, unique=True, max_length=100)
    
    # Hospital Reference (CRITICAL: Must exist before doctor registers)
    hospital = ReferenceField(Hospital, required=True, reverse_delete_rule=2)  # CASCADE delete
    
    # Contact
    phone = StringField(max_length=20)
    
    # Status
    is_active = BooleanField(default=True)
    registration_date = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'doctors',
        'indexes': [
            'username',
            'email',
            'license_number',
            'hospital',  # Index for quick hospital-doctor lookups
        ]
    }
    
    def __str__(self):
        return f"Dr. {self.name} ({self.hospital.name})"
    
    def clean(self):
        """
        Validation before saving.
        
        ENFORCES BUSINESS RULE:
        Doctors can only register if their hospital exists in database.
        """
        if not self.hospital:
            raise ValidationError("Doctor must be associated with a hospital")
        
        # Ensure hospital exists and is active
        if not self.hospital.is_active:
            raise ValidationError("Cannot register doctor for inactive hospital")


class HospitalDataset(Document):
    """
    Metadata about datasets uploaded by hospitals for federated learning.
    
    WHY STORE METADATA ONLY:
    - Privacy: Raw patient data never stored in central database
    - Compliance: Follows FL principle of local data storage
    - Scalability: Large CSV files stay on hospital's filesystem
    - Security: Reduces attack surface
    
    FL WORKFLOW:
    1. Hospital uploads CSV file to their local storage
    2. System creates this metadata record
    3. FL coordinator reads metadata to know which hospitals have data
    4. FL training happens locally at each hospital
    5. Only model weights are shared (not data)
    """
    
    hospital = ReferenceField(Hospital, required=True, reverse_delete_rule=2)
    
    # File Metadata
    file_name = StringField(required=True, max_length=255)
    file_path = StringField(required=True)  # Relative path from MEDIA_ROOT
    file_size = IntField()  # Size in bytes
    
    # Dataset Statistics
    num_records = IntField(default=0)
    num_features = IntField(default=0)
    
    # Schema Info (optional - can store column names as JSON string)
    schema_info = StringField()  # JSON string of column names and types
    
    # Timestamps
    upload_date = DateTimeField(default=datetime.utcnow)
    last_used = DateTimeField()  # When last used in FL training
    
    # Status
    is_processed = BooleanField(default=False)  # Has been validated and processed
    is_available_for_fl = BooleanField(default=False)  # Ready for FL training
    
    meta = {
        'collection': 'hospital_datasets',
        'indexes': [
            'hospital',
            'upload_date',
            {'fields': ['hospital', 'is_available_for_fl']},
        ],
        'ordering': ['-upload_date']
    }
    
    def __str__(self):
        return f"{self.file_name} ({self.hospital.name})"
    
    def mark_as_processed(self, num_records, num_features):
        """Mark dataset as processed and ready for FL"""
        self.num_records = num_records
        self.num_features = num_features
        self.is_processed = True
        self.is_available_for_fl = True
        self.save()
