"""
Hospital App Views
Hospital dashboard and dataset management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Hospital, HospitalDataset
from .forms import DatasetUploadForm
import logging

logger = logging.getLogger(__name__)


def _ensure_hospital_record(user):
    """Get or create a Hospital record for the user."""
    try:
        # If hospital already exists, return it
        if hasattr(user, 'hospital') and user.hospital:
            return user.hospital
        
        # Create Hospital record for the user
        hospital, created = Hospital.objects.get_or_create(
            user=user,
            defaults={
                'name': f'{user.first_name or user.username} Hospital',
                'address': 'Hospital Address',
                'city': 'City',
                'state': 'State',
                'pincode': '000000',
                'contact_number': '0000000000',
                'email': user.email or f'{user.username}@hospital.local',
                'registration_number': f'REG-{user.id}',
                'is_verified': True
            }
        )
        
        if created:
            logger.info('Auto-created Hospital record for user: %s', user.username)
        
        return hospital
    except Exception as exc:
        logger.error('Failed to ensure hospital record for %s: %s', user.username, exc)
        raise


def _is_hospital(request):
    """Check if user is a hospital (via Hospital model or session role from login)"""
    # Check Hospital model relationship (primary)
    if hasattr(request.user, 'hospital'):
        return True
    # Check session role set during login (fallback for test accounts)
    if request.session.get('user_role') == 'hospital':
        return True
    return False


@login_required
def hospital_dashboard(request):
    """Hospital dashboard - view datasets and upload new ones"""
    # Check if user is a hospital
    if not _is_hospital(request):
        messages.error(request, 'Access denied. Hospital account required.')
        return redirect('core:home')
    
    # Ensure hospital record exists
    hospital = _ensure_hospital_record(request.user)
    
    datasets = hospital.datasets.all()
    
    context = {
        'page_title': 'Hospital Dashboard - HeartFL',
        'hospital': hospital,
        'datasets': datasets,
        'total_datasets': datasets.count(),
        'total_doctors': hospital.doctors.count()
    }
    return render(request, 'hospitals/dashboard.html', context)


@login_required
def upload_dataset(request):
    """Upload dataset for federated learning"""
    # Check if user is a hospital
    if not _is_hospital(request):
        messages.error(request, 'Access denied. Hospital account required.')
        return redirect('core:home')
    
    # Ensure hospital record exists
    hospital = _ensure_hospital_record(request.user)
    
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.hospital = hospital
            dataset.save()
            messages.success(request, 'Dataset uploaded successfully!')
            return redirect('hospitals:dashboard')
    else:
        form = DatasetUploadForm()
    
    context = {
        'page_title': 'Upload Dataset - HeartFL',
        'form': form
    }
    return render(request, 'hospitals/upload_dataset.html', context)


@login_required
def view_dataset(request, dataset_id):
    """View dataset details"""
    # Check if user is a hospital
    if not _is_hospital(request):
        messages.error(request, 'Access denied.')
        return redirect('hospitals:dashboard')
    
    # Ensure hospital record exists
    hospital = _ensure_hospital_record(request.user)
    
    # Get dataset
    dataset = get_object_or_404(HospitalDataset, id=dataset_id)
    
    # Verify it belongs to the hospital user
    if dataset.hospital != hospital:
        messages.error(request, 'Access denied.')
        return redirect('hospitals:dashboard')
    
    context = {
        'page_title': 'Dataset Details - HeartFL',
        'dataset': dataset
    }
    return render(request, 'hospitals/view_dataset.html', context)
