"""
Hospital Forms - MONGODB INTEGRATED
====================================
"""
from django import forms


class DatasetUploadForm(forms.Form):
    """
    Form for uploading datasets to MongoDB.
    
    STORES:
    - File in MEDIA_ROOT/datasets/
    - Metadata in MongoDB HospitalDataset collection
    """
    
    dataset_file = forms.FileField(
        label='Dataset File (CSV)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text='Upload CSV file containing patient data for federated learning'
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional description of the dataset'
        })
    )
    
    def clean_dataset_file(self):
        """Validate uploaded file"""
        file = self.cleaned_data.get('dataset_file')
        
        if not file:
            raise forms.ValidationError("Please select a file to upload.")
        
        # Validate file extension
        if not file.name.endswith('.csv'):
            raise forms.ValidationError("Only CSV files are allowed.")
        
        # Validate file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50 MB
        if file.size > max_size:
            raise forms.ValidationError(f"File size too large. Maximum allowed: 50 MB")
        
        return file
