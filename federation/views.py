from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import FLRound, HospitalModel, GlobalModel
from .fl_utils import train_local_model, aggregate_models
from hospitals.models import Hospital, Dataset

@login_required
def round_list(request):
    rounds = FLRound.objects.all()
    return render(request, 'federation/round_list.html', {'rounds': rounds})

@login_required
def start_round(request):
    if request.user.role not in ['superadmin']:
        messages.error(request, 'Permission denied.')
        return redirect('federation:rounds')
    
    if request.method == 'POST':
        last_round = FLRound.objects.order_by('-round_number').first()
        round_number = (last_round.round_number + 1) if last_round else 1
        fl_round = FLRound.objects.create(round_number=round_number, status='training')
        
        hospitals_with_data = []
        for hospital in Hospital.objects.all():
            dataset = hospital.datasets.filter(status='ready').order_by('-uploaded_at').first()
            if dataset:
                hospitals_with_data.append((hospital, dataset))
        
        if not hospitals_with_data:
            messages.error(request, 'No hospitals with ready datasets found.')
            fl_round.status = 'failed'
            fl_round.save()
            return redirect('federation:rounds')
        
        hospital_weights = []
        for hospital, dataset in hospitals_with_data:
            try:
                weights, accuracy = train_local_model(dataset.csv_file.path)
                HospitalModel.objects.create(
                    fl_round=fl_round,
                    hospital=hospital,
                    local_accuracy=accuracy,
                    model_weights=weights
                )
                hospital_weights.append(weights)
            except Exception as e:
                messages.warning(request, f'Error training model for {hospital.name}: {e}')
        
        if hospital_weights:
            fl_round.status = 'aggregating'
            fl_round.save()
            global_weights = aggregate_models(hospital_weights)
            avg_accuracy = sum(hm.local_accuracy for hm in fl_round.hospital_models.all()) / len(hospital_weights)
            GlobalModel.objects.create(
                fl_round=fl_round,
                global_accuracy=avg_accuracy,
                model_weights=global_weights
            )
            fl_round.status = 'completed'
            fl_round.accuracy = avg_accuracy
            fl_round.participants_count = len(hospital_weights)
            fl_round.completed_at = timezone.now()
            fl_round.save()
            messages.success(request, f'FL Round {round_number} completed! Global accuracy: {avg_accuracy:.2%}')
        else:
            fl_round.status = 'failed'
            fl_round.save()
            messages.error(request, 'Failed to train any models.')
        
        return redirect('federation:round_detail', pk=fl_round.pk)
    
    return render(request, 'federation/start_round.html')

@login_required
def round_detail(request, pk):
    fl_round = get_object_or_404(FLRound, pk=pk)
    hospital_models = fl_round.hospital_models.all()
    global_model = fl_round.global_models.first()
    return render(request, 'federation/round_detail.html', {
        'round': fl_round,
        'hospital_models': hospital_models,
        'global_model': global_model,
    })
