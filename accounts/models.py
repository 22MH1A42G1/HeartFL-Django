from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('hospital_admin', 'Hospital Admin'),
        ('doctor', 'Doctor'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='doctor')
    
    def is_superadmin(self):
        return self.role == 'superadmin'
    
    def is_hospital_admin(self):
        return self.role == 'hospital_admin'
    
    def is_doctor(self):
        return self.role == 'doctor'
