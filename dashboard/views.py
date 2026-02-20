from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from hospitals.models import Hospital, Dataset
from federation.models import FLRound, GlobalModel
from predictions.models import Prediction
import json

@login_required
def index(request):
    total_hospitals = Hospital.objects.count()
    total_rounds = FLRound.objects.count()
    total_predictions = Prediction.objects.count()
    latest_model = GlobalModel.objects.order_by('-created_at').first()
    latest_accuracy = latest_model.global_accuracy if latest_model else 0
    
    completed_rounds = FLRound.objects.filter(status='completed').order_by('round_number')
    chart_labels = [f'Round {r.round_number}' for r in completed_rounds]
    chart_data = [round(r.accuracy * 100, 2) if r.accuracy else 0 for r in completed_rounds]
    
    recent_predictions = Prediction.objects.order_by('-created_at')[:5]
    recent_rounds = FLRound.objects.order_by('-started_at')[:5]
    
    context = {
        'total_hospitals': total_hospitals,
        'total_rounds': total_rounds,
        'total_predictions': total_predictions,
        'latest_accuracy': round(latest_accuracy * 100, 2),
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'recent_predictions': recent_predictions,
        'recent_rounds': recent_rounds,
    }
    return render(request, 'dashboard/index.html', context)
