"""
Federated Learning App Views - MONGODB INTEGRATED
==================================================
FL Dashboard and visualization using MongoDB queries
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from hospitals.documents import Hospital, HospitalDataset, Doctor
from federated.documents import FederatedRound, LocalModel
from prediction.documents import PredictionResult
from heartfl.db_utils import get_fl_dashboard_stats


def fl_dashboard(request):
    """
    Federated Learning Dashboard.
    
    MONGODB QUERIES:
    - Aggregates data from multiple collections
    - Shows hospital-wise statistics
    - Displays FL rounds and accuracy trends
    
    Visualizes the FL process: data upload → local training → aggregation → global model
    """
    # Get FL statistics from MongoDB
    stats = get_fl_dashboard_stats()
    
    # Get hospitals with datasets
    hospitals = Hospital.objects(is_active=True)
    hospitals_data = []
    
    for hospital in hospitals:
        dataset_count = HospitalDataset.objects(hospital=hospital).count()
        doctor_count = Doctor.objects(hospital=hospital).count()
        
        # Calculate total records from datasets
        datasets = HospitalDataset.objects(hospital=hospital)
        total_records = sum([d.num_records for d in datasets])
        
        hospitals_data.append({
            'name': hospital.name,
            'city': hospital.city,
            'datasets': dataset_count,
            'doctors': doctor_count,
            'records': total_records,
            'is_verified': hospital.is_verified
        })
    
    # Get federated rounds (latest 5)
    fl_rounds = FederatedRound.objects().order_by('-round_number')[:5]
    
    # FL process steps
    total_datasets = stats['hospitals_with_datasets']
    total_predictions = stats['total_predictions']
    
    fl_steps = [
        {
            'step': 1,
            'title': 'Dataset Upload',
            'description': 'Each hospital uploads its local dataset (patient records)',
            'icon': 'bi-cloud-upload',
            'status': 'completed' if total_datasets > 0 else 'pending'
        },
        {
            'step': 2,
            'title': 'Local Training',
            'description': 'Each hospital trains a local model on its private data',
            'icon': 'bi-cpu',
            'status': 'completed' if total_datasets > 0 else 'pending'
        },
        {
            'step': 3,
            'title': 'Model Update Sharing',
            'description': 'Hospitals share model weights (not raw data) with central server',
            'icon': 'bi-arrow-up-circle',
            'status': 'completed' if total_datasets > 0 else 'pending'
        },
        {
            'step': 4,
            'title': 'Global Aggregation',
            'description': 'Central server aggregates all local models into one global model',
            'icon': 'bi-diagram-3',
            'status': 'completed' if total_datasets > 0 else 'pending'
        },
        {
            'step': 5,
            'title': 'Global Model Update',
            'description': 'Updated global model is distributed back to all hospitals',
            'icon': 'bi-arrow-down-circle',
            'status': 'completed' if total_predictions > 0 else 'pending'
        },
    ]
    
    context = {
        'page_title': 'Federated Learning Dashboard - HeartFL',
        'active_page': 'fl_dashboard',
        'total_hospitals': stats['total_hospitals'],
        'active_hospitals': stats['active_hospitals'],
        'total_datasets': total_datasets,
        'total_predictions': total_predictions,
        'total_doctors': stats['total_doctors'],
        'fl_rounds': fl_rounds,
        'latest_round': stats.get('latest_round'),
        'hospitals_data': hospitals_data,
        'fl_steps': fl_steps
    }
    return render(request, 'federated/dashboard.html', context)


def fl_visualization(request):
    """
    FL Visualization page.
    
    MONGODB QUERIES:
    - Shows accuracy trends across FL rounds
    - Hospital participation metrics
    - Model convergence charts
    """
    # Get all FL rounds
    fl_rounds = FederatedRound.objects().order_by('round_number')
    
    # Prepare data for charts
    rounds_data = []
    for round in fl_rounds:
        rounds_data.append({
            'round_number': round.round_number,
            'accuracy': round.global_accuracy if round.global_accuracy else 0,
            'loss': round.global_loss if round.global_loss else 0,
            'participants': round.num_participants,
            'status': round.status
        })
    
    # Get local model statistics
    local_models = LocalModel.objects(is_submitted=True)
    hospital_performance = {}
    
    for model in local_models:
        hospital_name = model.hospital.name
        if hospital_name not in hospital_performance:
            hospital_performance[hospital_name] = {
                'rounds_participated': 0,
                'avg_accuracy': 0,
                'accuracies': []
            }
        
        hospital_performance[hospital_name]['rounds_participated'] += 1
        if model.local_accuracy:
            hospital_performance[hospital_name]['accuracies'].append(model.local_accuracy)
    
    # Calculate averages
    for hospital_name in hospital_performance:
        accuracies = hospital_performance[hospital_name]['accuracies']
        if accuracies:
            hospital_performance[hospital_name]['avg_accuracy'] = sum(accuracies) / len(accuracies)
    
    context = {
        'page_title': 'FL Visualization - HeartFL',
        'active_page': 'fl_dashboard',
        'rounds_data': rounds_data,
        'hospital_performance': hospital_performance
    }
    return render(request, 'federated/visualization.html', context)
