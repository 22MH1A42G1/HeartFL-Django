"""
MongoDB Document Models for Federated Learning App
===================================================

Tracks federated learning rounds and local model updates.

FEDERATED LEARNING WORKFLOW:
1. FL Coordinator initiates a training round
2. Each hospital trains local model on their data
3. Hospitals submit local model weights
4. Coordinator aggregates weights into global model
5. Global model distributed back to all hospitals

WHY MONGODB FOR FL METADATA:
- Flexible schema for different aggregation algorithms
- Easy to add new FL metrics without migrations
- Document model naturally fits distributed training logs
- Supports future extensions (differential privacy, secure aggregation)
"""

from mongoengine import (
    Document, StringField, IntField, FloatField, DictField,
    DateTimeField, ReferenceField, ListField, BooleanField
)
from datetime import datetime


class FederatedRound(Document):
    """
    Represents one round of federated learning.
    
    FL ROUND LIFECYCLE:
    1. initiated: Round created, waiting for hospitals
    2. training: Hospitals are training local models
    3. aggregating: Coordinator is aggregating model weights
    4. completed: Global model ready and distributed
    
    METRICS TRACKED:
    - num_participants: How many hospitals participated
    - global_accuracy: Accuracy of aggregated global model
    - round_duration: Time taken for complete round
    """
    
    round_number = IntField(required=True, unique=True)
    
    # Status
    status = StringField(
        required=True,
        choices=['initiated', 'training', 'aggregating', 'completed', 'failed'],
        default='initiated'
    )
    
    # Participating Hospitals
    participating_hospitals = ListField(ReferenceField('hospitals.Hospital'))
    num_participants = IntField(default=0)
    
    # FL Metrics
    global_accuracy = FloatField(min_value=0.0, max_value=1.0)
    global_loss = FloatField()
    
    # Timing
    start_time = DateTimeField(default=datetime.utcnow)
    end_time = DateTimeField()
    round_duration = IntField()  # Seconds
    
    # Model Info
    model_version = StringField(default='v1.0')
    aggregation_method = StringField(default='FedAvg')  # FedAvg, FedProx, etc.
    
    meta = {
        'collection': 'federated_rounds',
        'indexes': [
            '-round_number',
            'status',
        ],
        'ordering': ['-round_number']
    }
    
    def __str__(self):
        return f"FL Round {self.round_number} - {self.status}"
    
    def start_training(self):
        """Mark round as in training phase"""
        self.status = 'training'
        self.start_time = datetime.utcnow()
        self.save()
    
    def complete_round(self, accuracy, loss):
        """Mark round as completed with final metrics"""
        self.status = 'completed'
        self.end_time = datetime.utcnow()
        self.global_accuracy = accuracy
        self.global_loss = loss
        
        if self.start_time and self.end_time:
            self.round_duration = int((self.end_time - self.start_time).total_seconds())
        
        self.save()


class LocalModel(Document):
    """
    Represents a local model trained by a hospital in one FL round.
    
    WHY TRACK LOCAL MODELS:
    - Audit trail: Know which hospitals contributed to which rounds
    - Performance monitoring: Track local accuracy vs global accuracy
    - Debugging: Identify underperforming hospitals
    - Privacy: Ensure data stays local (only weights are shared)
    
    WEIGHTS STORAGE:
    - In production: Store in cloud storage (S3, GCS) and save URL here
    - For project: Store small weight diffs as JSON in weights_metadata
    """
    
    federated_round = ReferenceField(FederatedRound, required=True)
    hospital = ReferenceField('hospitals.Hospital', required=True)
    
    # Local Training Metrics
    local_accuracy = FloatField(min_value=0.0, max_value=1.0)
    local_loss = FloatField()
    num_samples_used = IntField()  # How many records from hospital's dataset
    
    # Model Weights (in production, this would be a URL to cloud storage)
    weights_metadata = DictField()  # Can store weight checksums, URLs, etc.
    
    # Training Details
    epochs_trained = IntField(default=1)
    learning_rate = FloatField(default=0.01)
    
    # Status
    is_submitted = BooleanField(default=False)
    submission_time = DateTimeField()
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'local_models',
        'indexes': [
            'federated_round',
            'hospital',
            {'fields': ['federated_round', 'hospital']},
        ]
    }
    
    def __str__(self):
        return f"{self.hospital.name} - Round {self.federated_round.round_number}"
    
    def submit_model(self, accuracy, loss, num_samples):
        """Mark local model as submitted for aggregation"""
        self.local_accuracy = accuracy
        self.local_loss = loss
        self.num_samples_used = num_samples
        self.is_submitted = True
        self.submission_time = datetime.utcnow()
        self.save()
