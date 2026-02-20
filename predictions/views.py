from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Prediction
from .forms import PredictionForm
from federation.models import GlobalModel
from federation.fl_utils import predict_risk

@login_required
def prediction_list(request):
    user = request.user
    if user.role == 'superadmin':
        predictions = Prediction.objects.all()
    else:
        predictions = Prediction.objects.filter(doctor=user)
    return render(request, 'predictions/list.html', {'predictions': predictions})

@login_required
def new_prediction(request):
    global_model = GlobalModel.objects.order_by('-created_at').first()
    if not global_model:
        messages.warning(request, 'No trained global model available yet. Please run a federated learning round first.')
        return redirect('predictions:list')
    
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            features = [
                float(form.cleaned_data['age']),
                float(form.cleaned_data['sex']),
                float(form.cleaned_data['cp']),
                float(form.cleaned_data['trestbps']),
                float(form.cleaned_data['chol']),
                float(form.cleaned_data['fbs']),
                float(form.cleaned_data['restecg']),
                float(form.cleaned_data['thalach']),
                float(form.cleaned_data['exang']),
                float(form.cleaned_data['oldpeak']),
                float(form.cleaned_data['slope']),
                float(form.cleaned_data['ca']),
                float(form.cleaned_data['thal']),
            ]
            try:
                risk_score = predict_risk(global_model.model_weights, features)
                pred_value = 1 if risk_score >= 0.5 else 0
                prediction = Prediction.objects.create(
                    doctor=request.user,
                    age=features[0], sex=features[1], cp=features[2],
                    trestbps=features[3], chol=features[4], fbs=features[5],
                    restecg=features[6], thalach=features[7], exang=features[8],
                    oldpeak=features[9], slope=features[10], ca=features[11],
                    thal=features[12],
                    risk_score=risk_score,
                    prediction=pred_value
                )
                messages.success(request, f'Prediction completed! Risk score: {risk_score:.1%}')
                return redirect('predictions:detail', pk=prediction.pk)
            except Exception as e:
                messages.error(request, f'Prediction error: {e}')
    else:
        form = PredictionForm()
    
    return render(request, 'predictions/new.html', {'form': form})

@login_required
def prediction_detail(request, pk):
    prediction = get_object_or_404(Prediction, pk=pk)
    return render(request, 'predictions/detail.html', {'prediction': prediction})
