"""
Accounts Forms
User registration forms for Hospital and Doctor
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from hospitals.models import Hospital, Doctor


class HospitalRegistrationForm(UserCreationForm):
    """Hospital registration form"""
    
    # User fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    
    # Hospital fields
    hospital_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital Name'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Full Address', 'rows': 3})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'})
    )
    pincode = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode'})
    )
    contact_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'})
    )
    registration_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital Registration Number'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                user_type='hospital',
                phone=self.cleaned_data['contact_number']
            )
            
            # Create Hospital
            Hospital.objects.create(
                user=user,
                name=self.cleaned_data['hospital_name'],
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                state=self.cleaned_data['state'],
                pincode=self.cleaned_data['pincode'],
                contact_number=self.cleaned_data['contact_number'],
                email=self.cleaned_data['email'],
                registration_number=self.cleaned_data['registration_number']
            )
        
        return user


class DoctorRegistrationForm(UserCreationForm):
    """Doctor registration form - must be linked to a registered hospital"""
    
    # User fields
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    
    # Doctor fields
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dr. Full Name'})
    )
    hospital = forms.ModelChoiceField(
        queryset=Hospital.objects.filter(is_verified=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="-- Select Hospital --"
    )
    specialization = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specialization (Optional)'})
    )
    license_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Medical License Number'})
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update hospital queryset to include all hospitals (remove is_verified filter for demo)
        self.fields['hospital'].queryset = Hospital.objects.all()
        if not Hospital.objects.exists():
            self.fields['hospital'].help_text = "No hospitals registered yet. Please register a hospital first."
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Create UserProfile
            UserProfile.objects.create(
                user=user,
                user_type='doctor',
                phone=self.cleaned_data['phone']
            )
            
            # Create Doctor
            Doctor.objects.create(
                user=user,
                hospital=self.cleaned_data['hospital'],
                full_name=self.cleaned_data['full_name'],
                specialization=self.cleaned_data.get('specialization', ''),
                license_number=self.cleaned_data['license_number'],
                phone=self.cleaned_data['phone'],
                email=self.cleaned_data['email']
            )
        
        return user
