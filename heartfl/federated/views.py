"""
Federated Learning App Views
FL Dashboard and visualization
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from hospitals.models import Hospital, HospitalDataset
from federated.models import FederatedRound, LocalModel
from prediction.models import PredictionResult


def fl_dashboard(request):
    """
    Federated Learning Dashboard
    Visualizes the FL process: data upload, local training, aggregation, global model
    """
    # Get FL statistics
    total_hospitals = Hospital.objects.count()
    total_datasets = HospitalDataset.objects.count()
    total_predictions = PredictionResult.objects.count()
    
    # Get hospitals with datasets
    hospitals = Hospital.objects.all()
    hospitals_data = []
    for hospital in hospitals:
        hospitals_data.append({
            'name': hospital.name,
            'datasets': hospital.datasets.count(),
            'doctors': hospital.doctors.count(),
            'records': sum([d.num_records for d in hospital.datasets.all()])
        })
    
    # Get federated rounds
    fl_rounds = FederatedRound.objects.all()[:5]  # Latest 5 rounds
    
    # FL process steps
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
        'total_hospitals': total_hospitals,
        'total_datasets': total_datasets,
        'total_predictions': total_predictions,
        'hospitals_data': hospitals_data,
        'fl_steps': fl_steps,
        'fl_rounds': fl_rounds
    }
    return render(request, 'federated/dashboard.html', context)


@login_required
def fl_visualization(request):
    """Detailed FL visualization with charts"""
    hospitals = Hospital.objects.all()
    fl_rounds = FederatedRound.objects.all()
    
    context = {
        'page_title': 'FL Visualization - HeartFL',
        'hospitals': hospitals,
        'fl_rounds': fl_rounds
    }
    return render(request, 'federated/visualization.html', context)
