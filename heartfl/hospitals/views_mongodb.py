"""
Hospital App Views - MONGODB INTEGRATED
========================================

MONGODB QUERIES:
- Hospital.objects(username=...) instead of request.user.hospital
- HospitalDataset.objects(hospital=...) for filtering datasets
- Doctor.objects(hospital=...) for doctor count
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from hospitals.documents import Hospital, HospitalDataset, Doctor
from .forms_mongodb import DatasetUploadForm
import pandas as pd
import os
from django.conf import settings


@login_required
def hospital_dashboard(request):
    """
    Hospital dashboard - view datasets and upload new ones.
    
    MONGODB QUERY:
    - Find Hospital by username
    - Count datasets for this hospital
    - Count doctors linked to this hospital
    """
    # Get hospital from MongoDB
    hospital = Hospital.objects(username=request.user.username).first()
    
    if not hospital:
        messages.error(request, 'Hospital profile not found. Please register as a hospital.')
        return redirect('accounts:hospital_register')
    
    # Get all datasets for this hospital
    datasets = HospitalDataset.objects(hospital=hospital).order_by('-upload_date')
    
    # Get doctors count
    doctors_count = Doctor.objects(hospital=hospital).count()
    
    context = {
        'page_title': 'Hospital Dashboard - HeartFL',
        'hospital': hospital,
        'datasets': datasets,
        'total_datasets': datasets.count(),
        'total_doctors': doctors_count
    }
    return render(request, 'hospitals/dashboard.html', context)


@login_required
def upload_dataset(request):
    """
    Upload dataset for federated learning.
    
    PROCESS:
    1. Save uploaded CSV file
    2. Parse file to get statistics (rows, columns)
    3. Create HospitalDataset document in MongoDB
    4. Store only metadata (not raw data)
    """
    # Get hospital from MongoDB
    hospital = Hospital.objects(username=request.user.username).first()
    
    if not hospital:
        messages.error(request, 'Hospital profile not found.')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['dataset_file']
            description = form.cleaned_data.get('description', '')
            
            # Save file
            import time
            timestamp = int(time.time())
            filename = f"{hospital.registration_number}_{timestamp}_{uploaded_file.name}"
            file_path = os.path.join('datasets', filename)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # Create directory if not exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Save file
            with open(full_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Parse CSV to get statistics
            try:
                df = pd.read_csv(full_path)
                num_records = len(df)
                num_features = len(df.columns)
                schema_info = str(df.columns.tolist())
            except Exception as e:
                num_records = 0
                num_features = 0
                schema_info = f"Error parsing file: {str(e)}"
            
            # Create dataset document in MongoDB
            dataset = HospitalDataset(
                hospital=hospital,
                file_name=uploaded_file.name,
                file_path=file_path,
                file_size=uploaded_file.size,
                num_records=num_records,
                num_features=num_features,
                schema_info=schema_info,
                is_processed=True if num_records > 0 else False,
                is_available_for_fl=True if num_records > 0 else False
            )
            dataset.save()
            
            messages.success(request, f'Dataset uploaded successfully! {num_records} records, {num_features} features.')
            return redirect('hospitals:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DatasetUploadForm()
    
    context = {
        'page_title': 'Upload Dataset - HeartFL',
        'form': form
    }
    return render(request, 'hospitals/upload_dataset.html', context)


@login_required
def view_dataset(request, dataset_id):
    """
    View dataset details.
    
    MONGODB QUERY:
    - Get HospitalDataset by ID
    - Verify ownership before displaying
    """
    # Get hospital from MongoDB
    hospital = Hospital.objects(username=request.user.username).first()
    
    if not hospital:
        messages.error(request, 'Access denied.')
        return redirect('core:home')
    
    # Get dataset from MongoDB
    dataset = HospitalDataset.objects(id=dataset_id, hospital=hospital).first()
    
    if not dataset:
        messages.error(request, 'Dataset not found or access denied.')
        return redirect('hospitals:dashboard')
    
    context = {
        'page_title': 'Dataset Details - HeartFL',
        'dataset': dataset
    }
    return render(request, 'hospitals/view_dataset.html', context)
