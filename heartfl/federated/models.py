"""
Federated Learning Models
Tracks training rounds and model aggregation
"""
from django.db import models
from hospitals.models import Hospital


class FederatedRound(models.Model):
    """
    Represents a complete federated learning training round
    Tracks global model updates across all participating hospitals
    """
    round_number = models.IntegerField(unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    # Metrics
    global_accuracy = models.FloatField(default=0.0)
    global_loss = models.FloatField(default=0.0)
    participating_hospitals = models.IntegerField(default=0)
    
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-round_number']
        verbose_name = 'Federated Learning Round'
        verbose_name_plural = 'Federated Learning Rounds'
    
    def __str__(self):
        return f"Round {self.round_number} - {'Completed' if self.is_completed else 'In Progress'}"


class LocalModel(models.Model):
    """
    Represents a local model trained by each hospital
    Stores training metrics for visualization
    """
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='local_models')
    federated_round = models.ForeignKey(FederatedRound, on_delete=models.CASCADE, related_name='local_models')
    
    # Training metrics
    accuracy = models.FloatField(default=0.0)
    loss = models.FloatField(default=0.0)
    training_samples = models.IntegerField(default=0)
    epochs_trained = models.IntegerField(default=1)
    
    # Timestamps
    training_started = models.DateTimeField(auto_now_add=True)
    training_completed = models.DateTimeField(null=True, blank=True)
    is_uploaded = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-training_started']
        verbose_name = 'Local Model'
        verbose_name_plural = 'Local Models'
    
    def __str__(self):
        return f"{self.hospital.name} - Round {self.federated_round.round_number}"
