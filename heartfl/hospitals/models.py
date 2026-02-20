"""
Hospital Models
Manages hospital registration and dataset uploads for federated learning
"""
from django.db import models
from django.contrib.auth.models import User
import os


def hospital_dataset_path(instance, filename):
    """Generate upload path for hospital datasets"""
    return f'hospital_datasets/{instance.hospital.name}/{filename}'


class Hospital(models.Model):
    """
    Hospital model representing a federated learning node
    Each hospital can upload datasets and train local models
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hospital')
    name = models.CharField(max_length=200, unique=True, help_text="Hospital Name")
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    registration_number = models.CharField(max_length=50, unique=True, help_text="Hospital Registration Number")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Hospital'
        verbose_name_plural = 'Hospitals'
    
    def __str__(self):
        return self.name
    
    def total_datasets(self):
        return self.datasets.count()
    
    def total_doctors(self):
        return self.doctors.count()


class HospitalDataset(models.Model):
    """
    Dataset uploaded by hospitals for federated learning
    Each dataset represents training data for the local model
    """
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='datasets')
    dataset_file = models.FileField(upload_to=hospital_dataset_path)
    description = models.TextField(blank=True, null=True)
    num_records = models.IntegerField(default=0, help_text="Number of patient records")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Hospital Dataset'
        verbose_name_plural = 'Hospital Datasets'
    
    def __str__(self):
        return f"{self.hospital.name} - Dataset {self.id}"
    
    def filename(self):
        return os.path.basename(self.dataset_file.name)


class Doctor(models.Model):
    """
    Doctor model linked to a hospital
    Doctors can perform predictions using the global federated model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors')
    full_name = models.CharField(max_length=200)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['full_name']
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'
    
    def __str__(self):
        return f"Dr. {self.full_name} ({self.hospital.name})"
