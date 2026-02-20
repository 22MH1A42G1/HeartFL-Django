from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import pandas as pd
from .models import Hospital, Dataset
from .forms import HospitalForm, DatasetUploadForm

@login_required
def hospital_list(request):
    user = request.user
    if user.role == 'superadmin':
        hospitals = Hospital.objects.all()
    elif user.role == 'hospital_admin':
        hospitals = Hospital.objects.filter(hospital_admin=user)
    else:
        hospitals = Hospital.objects.all()
    
    form = HospitalForm()
    if request.method == 'POST' and user.role == 'superadmin':
        form = HospitalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hospital created successfully!')
            return redirect('hospitals:list')
    
    return render(request, 'hospitals/list.html', {'hospitals': hospitals, 'form': form})

@login_required
def hospital_detail(request, pk):
    hospital = get_object_or_404(Hospital, pk=pk)
    datasets = hospital.datasets.order_by('-uploaded_at')
    return render(request, 'hospitals/detail.html', {'hospital': hospital, 'datasets': datasets})

@login_required
def upload_dataset(request):
    user = request.user
    if user.role == 'hospital_admin':
        try:
            hospital = user.hospital
        except Hospital.DoesNotExist:
            messages.error(request, 'No hospital assigned to your account.')
            return redirect('hospitals:list')
    elif user.role == 'superadmin':
        hospitals = Hospital.objects.all()
        hospital = hospitals.first()
    else:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = DatasetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            if user.role == 'superadmin':
                hospital_id = request.POST.get('hospital_id')
                if hospital_id:
                    dataset.hospital = get_object_or_404(Hospital, pk=hospital_id)
                else:
                    dataset.hospital = hospital
            else:
                dataset.hospital = hospital
            dataset.save()
            
            try:
                df = pd.read_csv(dataset.csv_file.path)
                dataset.rows_count = len(df)
                dataset.status = 'ready'
                dataset.save()
                messages.success(request, f'Dataset uploaded successfully with {len(df)} rows!')
            except Exception as e:
                dataset.status = 'error'
                dataset.error_message = str(e)
                dataset.save()
                messages.error(request, f'Error processing CSV: {e}')
            
            return redirect('hospitals:detail', pk=dataset.hospital.pk)
    else:
        form = DatasetUploadForm()
    
    hospitals = Hospital.objects.all() if user.role == 'superadmin' else None
    return render(request, 'hospitals/upload.html', {'form': form, 'hospitals': hospitals})
