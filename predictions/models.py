from django.db import models
from accounts.models import User

class Prediction(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    age = models.FloatField()
    sex = models.FloatField()
    cp = models.FloatField()
    trestbps = models.FloatField()
    chol = models.FloatField()
    fbs = models.FloatField()
    restecg = models.FloatField()
    thalach = models.FloatField()
    exang = models.FloatField()
    oldpeak = models.FloatField()
    slope = models.FloatField()
    ca = models.FloatField()
    thal = models.FloatField()
    risk_score = models.FloatField()
    prediction = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def risk_percentage(self):
        return round(self.risk_score * 100, 1)
    
    def risk_label(self):
        if self.risk_score >= 0.7:
            return 'High'
        elif self.risk_score >= 0.4:
            return 'Medium'
        return 'Low'
    
    def __str__(self):
        return f"Prediction by {self.doctor.username} - {self.created_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-created_at']
