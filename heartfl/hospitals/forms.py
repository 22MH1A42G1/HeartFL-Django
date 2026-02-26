"""
Hospital Forms
Dataset upload and hospital management forms
"""
from django import forms
from .models import HospitalDataset


class DatasetUploadForm(forms.ModelForm):
    """Form for hospitals to upload training datasets"""
    
    class Meta:
        model = HospitalDataset
        fields = ['dataset_file', 'description', 'num_records']
        widgets = {
            'dataset_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.csv',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description of the dataset (optional)',
                'rows': 3
            }),
            'num_records': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Number of patient records',
                'min': 1
            }),
        }
        labels = {
            'dataset_file': 'Upload Dataset (CSV)',
            'description': 'Dataset Description',
            'num_records': 'Number of Records'
        }
