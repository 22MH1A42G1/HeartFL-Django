"""
Accounts Forms - MONGODB INTEGRATED
====================================
User registration forms for Hospital and Doctor

HYBRID APPROACH:
- Django User: Created in SQLite (for auth)
- UserProfile: Created in MongoDB (user metadata)
- Hospital/Doctor: Created in MongoDB (application data)
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from accounts.documents import UserProfile
from hospitals.documents import Hospital, Doctor


class HospitalRegistrationForm(UserCreationForm):
    """
    Hospital registration form.
    
    CREATES 3 RECORDS:
    1. Django User (SQLite) - for authentication
    2. UserProfile (MongoDB) - links user to user_type
    3. Hospital (MongoDB) - hospital details
    """
    
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
    
    def clean_username(self):
        """Validate username doesn't exist in MongoDB"""
        username = self.cleaned_data.get('username')
        
        # Check Django User
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        
        # Check MongoDB UserProfile
        if UserProfile.objects(username=username).first():
            raise forms.ValidationError("Username already exists in system.")
        
        return username
    
    def clean_email(self):
        """Validate email doesn't exist in MongoDB"""
        email = self.cleaned_data.get('email')
        
        # Check MongoDB Hospital
        if Hospital.objects(email=email).first():
            raise forms.ValidationError("Email already registered.")
        
        return email
    
    def clean_registration_number(self):
        """Validate registration number is unique"""
        reg_num = self.cleaned_data.get('registration_number')
        
        if Hospital.objects(registration_number=reg_num).first():
            raise forms.ValidationError("Registration number already exists.")
        
        return reg_num
    
    def save(self, commit=True):
        """
        Save user and create MongoDB documents.
        
        TRANSACTION:
        1. Create Django User (SQLite)
        2. Create UserProfile (MongoDB)
        3. Create Hospital (MongoDB)
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Create UserProfile in MongoDB
            UserProfile(
                username=user.username,
                email=user.email,
                user_type='hospital',
                phone=self.cleaned_data['contact_number']
            ).save()
            
            # Create Hospital in MongoDB
            Hospital(
                username=user.username,
                email=user.email,
                name=self.cleaned_data['hospital_name'],
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                state=self.cleaned_data['state'],
                pincode=self.cleaned_data['pincode'],
                contact_number=self.cleaned_data['contact_number'],
                registration_number=self.cleaned_data['registration_number']
            ).save()
        
        return user


class DoctorRegistrationForm(UserCreationForm):
    """
    Doctor registration form - must be linked to a registered hospital.
    
    ENFORCEMENT:
    - Hospital field populated from MongoDB Hospital collection
    - Validation ensures hospital exists before doctor can register
    
    CREATES 3 RECORDS:
    1. Django User (SQLite) - for authentication
    2. UserProfile (MongoDB) - links user to user_type
    3. Doctor (MongoDB) - doctor details with hospital reference
    """
    
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
    hospital = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-control'}),
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
        
        # Populate hospital choices from MongoDB
        hospitals = Hospital.objects(is_active=True)
        hospital_choices = [('', '-- Select Hospital --')]
        hospital_choices += [(str(h.id), f"{h.name} ({h.city})") for h in hospitals]
        
        self.fields['hospital'].choices = hospital_choices
        
        if not hospitals:
            self.fields['hospital'].help_text = "No hospitals registered yet. Please register a hospital first."
    
    def clean_username(self):
        """Validate username doesn't exist"""
        username = self.cleaned_data.get('username')
        
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        
        if UserProfile.objects(username=username).first():
            raise forms.ValidationError("Username already exists in system.")
        
        return username
    
    def clean_email(self):
        """Validate email doesn't exist"""
        email = self.cleaned_data.get('email')
        
        if Doctor.objects(email=email).first():
            raise forms.ValidationError("Email already registered.")
        
        return email
    
    def clean_license_number(self):
        """Validate license number is unique"""
        license_num = self.cleaned_data.get('license_number')
        
        if Doctor.objects(license_number=license_num).first():
            raise forms.ValidationError("License number already exists.")
        
        return license_num
    
    def clean_hospital(self):
        """Validate hospital selection"""
        hospital_id = self.cleaned_data.get('hospital')
        
        if not hospital_id:
            raise forms.ValidationError("Please select a hospital.")
        
        # Verify hospital exists in MongoDB
        hospital = Hospital.objects(id=hospital_id).first()
        if not hospital:
            raise forms.ValidationError("Selected hospital does not exist.")
        
        if not hospital.is_active:
            raise forms.ValidationError("Selected hospital is not active.")
        
        return hospital_id
    
    def save(self, commit=True):
        """
        Save user and create MongoDB documents.
        
        TRANSACTION:
        1. Create Django User (SQLite)
        2. Create UserProfile (MongoDB)
        3. Create Doctor (MongoDB) with hospital reference
        """
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Get hospital document from MongoDB
            hospital_id = self.cleaned_data['hospital']
            hospital = Hospital.objects(id=hospital_id).first()
            
            # Create UserProfile in MongoDB
            UserProfile(
                username=user.username,
                email=user.email,
                user_type='doctor',
                phone=self.cleaned_data['phone']
            ).save()
            
            # Create Doctor in MongoDB with hospital reference
            Doctor(
                username=user.username,
                email=user.email,
                name=self.cleaned_data['full_name'],
                specialization=self.cleaned_data.get('specialization', ''),
                license_number=self.cleaned_data['license_number'],
                phone=self.cleaned_data['phone'],
                hospital=hospital  # ReferenceField to Hospital document
            ).save()
        
        return user
