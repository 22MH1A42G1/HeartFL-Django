from django import forms

class PredictionForm(forms.Form):
    age = forms.FloatField(label='Age', min_value=1, max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '63'}))
    sex = forms.ChoiceField(label='Sex', choices=[(1, 'Male'), (0, 'Female')],
        widget=forms.Select(attrs={'class': 'form-select'}))
    cp = forms.ChoiceField(label='Chest Pain Type', 
        choices=[(0,'Typical Angina'),(1,'Atypical Angina'),(2,'Non-anginal Pain'),(3,'Asymptomatic')],
        widget=forms.Select(attrs={'class': 'form-select'}))
    trestbps = forms.FloatField(label='Resting Blood Pressure (mm Hg)', min_value=50, max_value=250,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '145'}))
    chol = forms.FloatField(label='Serum Cholesterol (mg/dl)', min_value=100, max_value=600,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '233'}))
    fbs = forms.ChoiceField(label='Fasting Blood Sugar > 120 mg/dl', choices=[(1,'Yes'),(0,'No')],
        widget=forms.Select(attrs={'class': 'form-select'}))
    restecg = forms.ChoiceField(label='Resting ECG', 
        choices=[(0,'Normal'),(1,'ST-T Wave Abnormality'),(2,'Left Ventricular Hypertrophy')],
        widget=forms.Select(attrs={'class': 'form-select'}))
    thalach = forms.FloatField(label='Max Heart Rate Achieved', min_value=50, max_value=250,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '150'}))
    exang = forms.ChoiceField(label='Exercise Induced Angina', choices=[(1,'Yes'),(0,'No')],
        widget=forms.Select(attrs={'class': 'form-select'}))
    oldpeak = forms.FloatField(label='ST Depression (oldpeak)', min_value=0, max_value=10,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': '2.3'}))
    slope = forms.ChoiceField(label='Slope of Peak Exercise ST', 
        choices=[(0,'Upsloping'),(1,'Flat'),(2,'Downsloping')],
        widget=forms.Select(attrs={'class': 'form-select'}))
    ca = forms.ChoiceField(label='Number of Major Vessels (0-3)', choices=[(0,0),(1,1),(2,2),(3,3)],
        widget=forms.Select(attrs={'class': 'form-select'}))
    thal = forms.ChoiceField(label='Thalassemia', 
        choices=[(1,'Normal'),(2,'Fixed Defect'),(3,'Reversable Defect')],
        widget=forms.Select(attrs={'class': 'form-select'}))
