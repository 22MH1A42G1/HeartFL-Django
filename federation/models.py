from django.db import models
from hospitals.models import Hospital

class FLRound(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('training', 'Training'),
        ('aggregating', 'Aggregating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    round_number = models.IntegerField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    participants_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Round {self.round_number} - {self.status}"
    
    def accuracy_percent(self):
        return round(self.accuracy * 100, 1) if self.accuracy else 0
    
    class Meta:
        ordering = ['-round_number']

class HospitalModel(models.Model):
    fl_round = models.ForeignKey(FLRound, on_delete=models.CASCADE, related_name='hospital_models')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    local_accuracy = models.FloatField(default=0.0)
    trained_at = models.DateTimeField(auto_now_add=True)
    model_weights = models.JSONField(default=dict)
    
    def __str__(self):
        return f"Round {self.fl_round.round_number} - {self.hospital.name}"
    
    def local_accuracy_percent(self):
        return round(self.local_accuracy * 100, 1)

class GlobalModel(models.Model):
    fl_round = models.ForeignKey(FLRound, on_delete=models.CASCADE, related_name='global_models')
    global_accuracy = models.FloatField(default=0.0)
    model_weights = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Global Model - Round {self.fl_round.round_number}"
    
    def global_accuracy_percent(self):
        return round(self.global_accuracy * 100, 1)
