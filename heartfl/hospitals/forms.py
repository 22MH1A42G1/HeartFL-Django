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

    def clean_dataset_file(self):
        dataset_file = self.cleaned_data.get('dataset_file')
        if not dataset_file:
            return dataset_file

        filename = dataset_file.name.lower()
        if not filename.endswith('.csv'):
            raise forms.ValidationError('Please upload a CSV file.')

        return dataset_file
