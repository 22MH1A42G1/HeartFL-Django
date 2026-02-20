from django.db import models
from accounts.models import User

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    hospital_admin = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='hospital')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    @property
    def dataset_count(self):
        return self.datasets.count()
    
    @property
    def latest_dataset(self):
        return self.datasets.order_by('-uploaded_at').first()

class Dataset(models.Model):
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
    ]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='datasets')
    csv_file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    rows_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    error_message = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.hospital.name} - {self.uploaded_at.strftime('%Y-%m-%d')}"
