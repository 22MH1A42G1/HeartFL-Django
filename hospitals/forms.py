from django import forms
from .models import Hospital, Dataset

class HospitalForm(forms.ModelForm):
    class Meta:
        model = Hospital
        fields = ['name', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['csv_file']
        widgets = {
            'csv_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'}),
        }
