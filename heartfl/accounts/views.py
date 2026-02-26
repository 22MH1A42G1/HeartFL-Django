"""
Accounts App Views
User authentication - Login, Register, Logout
"""
import logging
import os
import random
import time
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from .forms import HospitalRegistrationForm, DoctorRegistrationForm, ThemeSettingsForm
from .models import UserProfile, UserThemeSettings
from hospitals.models import Hospital, Doctor
from prediction.models import PredictionResult
from accounts.models import UserProfile


logger = logging.getLogger(__name__)


def _detect_contact_type(contact: str) -> str:
    """Return 'email', 'phone', or 'unknown' based on the input string."""
    contact = contact.strip()
    if '@' in contact and '.' in contact.split('@')[-1]:
        return 'email'
    # Phone: remove spaces, dashes, parentheses, plus signs
    digits_only = ''.join(ch for ch in contact if ch.isdigit())
    if digits_only and 10 <= len(digits_only) <= 15:
        return 'phone'
    return 'unknown'


def _send_sms_otp(phone: str, otp: str) -> bool:
    """Send OTP via SMS using Twilio-style credentials if configured. Fails silently."""
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_FROM_NUMBER')

    if not all([account_sid, auth_token, from_number]):
        logger.info('SMS not sent; Twilio credentials missing. Phone=%s OTP=%s', phone, otp)
        return False

    try:
        # Lazy import to avoid hard dependency if Twilio is unavailable
        from twilio.rest import Client  # type: ignore

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=f'HeartFL OTP: {otp}',
            from_=from_number,
            to=phone,
        )
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning('SMS send failed for %s: %s', phone, exc)
        return False


def user_login(request):
    """
    User login with role-based redirect.
    - Doctor → Doctor Dashboard
    - Hospital → Hospital Dashboard
    - Admin → Admin Dashboard
    Falls back to username pattern if MongoDB profile not found.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Detect user role
                user_role = 'user'
                redirect_url = 'accounts:dashboard'
                
                # 1. Try to get role from MongoDB UserProfile
                try:
                    profile = UserProfile.objects(username=username).first()
                    if profile and profile.user_type:
                        user_role = profile.user_type
                        logger.info('User %s logged in with role: %s (from profile)', username, user_role)
                except Exception as exc:  # noqa: BLE001
                    logger.warning('Could not fetch profile for %s: %s', username, exc)
                    
                    # 2. Fallback: Detect role from username pattern
                    if 'doctor' in username.lower():
                        user_role = 'doctor'
                        logger.info('User %s detected as doctor (from username)', username)
                    elif 'hospital' in username.lower():
                        user_role = 'hospital'
                        logger.info('User %s detected as hospital (from username)', username)
                    elif user.is_superuser:
                        user_role = 'admin'
                
                # Set welcome message based on role
                if user_role == 'doctor':
                    messages.success(request, f'Welcome, Dr. {user.first_name or username}!')
                    redirect_url = 'accounts:dashboard'
                elif user_role == 'hospital':
                    messages.success(request, f'Welcome, {user.first_name or username}!')
                    redirect_url = 'accounts:dashboard'
                elif user.is_superuser or user_role == 'admin':
                    messages.success(request, 'Welcome, Admin!')
                    redirect_url = 'admin:index'
                else:
                    messages.success(request, f'Welcome back, {user.username}!')
                
                # Store role in session for dashboard access
                request.session['user_role'] = user_role
                logger.info('User %s session role set to: %s', username, user_role)
                
                return redirect(redirect_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    context = {
        'page_title': 'Login - HeartFL',
        'active_page': 'login',
        'form': form
    }
    return render(request, 'accounts/login.html', context)


def forgot_password(request):
    """Forgot password with email/phone OTP, session storage, and 10-min expiration."""
    # Check if OTP exists and hasn't expired (10 minutes = 600 seconds)
    otp_timestamp = request.session.get('otp_timestamp')
    otp_sent = False
    if otp_timestamp and (time.time() - otp_timestamp) < 600:
        otp_sent = True
    elif otp_timestamp:
        # OTP expired, clear session
        for key in ['otp', 'contact', 'contact_type', 'otp_timestamp', 'otp_verified']:
            request.session.pop(key, None)
        messages.warning(request, 'OTP expired. Please request a new one.')
    
    target_contact = request.session.get('contact')

    if request.method == 'POST':
        action = request.POST.get('action')
        contact = (request.POST.get('contact') or '').strip()

        if action == 'send_otp':
            if not contact:
                messages.error(request, 'Please enter your email or phone number.')
                return redirect('accounts:forgot_password')

            contact_type = _detect_contact_type(contact)
            if contact_type == 'unknown':
                messages.error(request, 'Enter a valid email address or phone number.')
                return redirect('accounts:forgot_password')

            # Generate 6-digit OTP
            otp = f"{random.randint(100000, 999999)}"
            request.session['otp'] = otp
            request.session['contact'] = contact
            request.session['contact_type'] = contact_type
            request.session['otp_timestamp'] = time.time()
            request.session['otp_verified'] = False
            otp_sent = True
            target_contact = contact

            if contact_type == 'email':
                try:
                    send_mail(
                        subject='HeartFL Password Reset OTP',
                        message=(
                            f'Your one-time password (OTP) for HeartFL password reset is:\n\n'
                            f'{otp}\n\n'
                            f'This OTP will expire in 10 minutes.\n\n'
                            f'If you did not request this, please ignore this email.'
                        ),
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
                        recipient_list=[contact],
                        fail_silently=False,
                    )
                    messages.success(request, f'OTP sent to {contact}. Check your inbox or spam folder.')
                    logger.info('OTP sent successfully to %s', contact)
                except Exception as exc:  # noqa: BLE001
                    error_msg = str(exc)
                    logger.error('Email send failed for %s: %s', contact, error_msg)
                    
                    # Provide specific troubleshooting based on error
                    if 'Username and Password not accepted' in error_msg or 'Authentication failed' in error_msg:
                        help_text = (
                            f'Gmail authentication failed. You must use an App Password:\n'
                            f'1. Go to https://myaccount.google.com/apppasswords\n'
                            f'2. Generate a 16-character App Password\n'
                            f'3. Update EMAIL_HOST_PASSWORD in .env with this password\n\n'
                            f'Test OTP (use this for now): {otp}'
                        )
                    elif 'SMTPServerDisconnected' in error_msg or 'Connection refused' in error_msg:
                        help_text = (
                            f'Cannot connect to Gmail server. Check your internet connection.\n'
                            f'Test OTP: {otp}'
                        )
                    else:
                        help_text = f'Email failed: {error_msg}\nTest OTP: {otp}'
                    
                    messages.warning(request, help_text)

            elif contact_type == 'phone':
                sent_sms = _send_sms_otp(contact, otp)
                if sent_sms:
                    messages.success(request, f'OTP sent to {contact}.')
                else:
                    messages.warning(request, f'SMS not configured. Test OTP: {otp}')

        elif action == 'verify_otp':
            otp_value = request.POST.get('otp', '').strip()
            session_otp = request.session.get('otp')
            otp_timestamp = request.session.get('otp_timestamp')

            # Validate OTP format
            if not otp_value or not otp_value.isdigit() or len(otp_value) != 6:
                messages.error(request, 'Please enter a valid 6-digit OTP.')
                return redirect('accounts:forgot_password')

            # Check expiration
            if not otp_timestamp or (time.time() - otp_timestamp) >= 600:
                for key in ['otp', 'contact', 'contact_type', 'otp_timestamp', 'otp_verified']:
                    request.session.pop(key, None)
                messages.error(request, 'OTP expired. Please request a new one.')
                return redirect('accounts:forgot_password')

            # Verify OTP
            if otp_value == session_otp:
                request.session['otp_verified'] = True
                messages.success(request, 'OTP verified successfully! Please set your new password.')
                return redirect('accounts:reset_password')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
        else:
            messages.error(request, 'Invalid request.')

    context = {
        'page_title': 'Forgot Password - HeartFL',
        'active_page': 'forgot',
        'otp_sent': otp_sent,
        'target_contact': target_contact,
    }
    return render(request, 'accounts/forgot.html', context)


def reset_password(request):
    """Reset password after OTP verification and sync with MongoDB via PyMongo."""
    # Check OTP verification status
    if not request.session.get('otp_verified'):
        messages.warning(request, 'Please verify OTP first to reset your password.')
        return redirect('accounts:forgot_password')

    # Check OTP hasn't expired during reset
    otp_timestamp = request.session.get('otp_timestamp')
    if not otp_timestamp or (time.time() - otp_timestamp) >= 600:
        for key in ['otp', 'contact', 'contact_type', 'otp_timestamp', 'otp_verified']:
            request.session.pop(key, None)
        messages.error(request, 'Session expired. Please start again.')
        return redirect('accounts:forgot_password')

    contact = request.session.get('contact')
    contact_type = request.session.get('contact_type')

    if request.method == 'POST':
        new_password = (request.POST.get('new_password') or '').strip()
        confirm_password = (request.POST.get('confirm_password') or '').strip()

        # Validation
        if not new_password or not confirm_password:
            messages.error(request, 'Both password fields are required.')
        elif new_password != confirm_password:
            messages.error(request, 'Passwords do not match. Please try again.')
        elif len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
        elif new_password.isdigit():
            messages.error(request, 'Password cannot be all numbers. Include letters.')
        elif new_password.isalpha():
            messages.error(request, 'Password cannot be all letters. Include numbers or symbols.')
        else:
            # Find user by email or username
            user = None
            if contact_type == 'email' and contact:
                user = User.objects.filter(email=contact).first()
            if not user and contact:
                user = User.objects.filter(username=contact).first()

            if not user:
                messages.error(request, 'Account not found. Please contact support.')
                logger.warning('Password reset attempted for non-existent account: %s', contact)
            else:
                # Update Django auth password
                user.set_password(new_password)
                user.save()
                logger.info('Password reset successful for user: %s', user.username)

                # Clear all OTP session data
                for key in ['otp', 'contact', 'contact_type', 'otp_timestamp', 'otp_verified']:
                    request.session.pop(key, None)

                messages.success(request, 'Password reset successfully! You can now log in with your new password.')
                return redirect('accounts:login')

    context = {
        'page_title': 'Reset Password - HeartFL',
        'active_page': 'reset',
        'contact': contact,
    }
    return render(request, 'accounts/reset.html', context)


@login_required
def user_dashboard(request):
    """
    Role-based dashboard:
    - Doctor: Shows patient predictions, model accuracy, FL insights
    - Hospital: Shows hospital data, doctor list, dataset upload
    - Other: General dashboard
    Gets role from MongoDB profile OR session (fallback).
    """
    user_role = request.session.get('user_role', 'user')
    profile = getattr(request.user, 'profile', None)

    if profile and profile.user_type:
        user_role = profile.user_type
        logger.info('Dashboard: %s role from SQL profile: %s', request.user.username, user_role)
    else:
        logger.info('Dashboard: %s using session role: %s', request.user.username, user_role)
    
    # Common data for all users
    prediction_history = []

    insights = {
        'accuracy': '92%',
        'latency': '1.8s avg',
        'notes': 'Insights will expand as more predictions are recorded.'
    }

    # Role-specific context
    if user_role == 'doctor':
        doctor = getattr(request.user, 'doctor', None)
        if doctor is None:
            doctor = Doctor.objects.filter(user=request.user).first()

        prediction_results = []
        prediction_count = 0
        if doctor:
            prediction_results = (
                PredictionResult.objects
                .filter(doctor=doctor)
                .select_related('patient_data')
                .order_by('-predicted_at')[:5]
            )
            prediction_count = PredictionResult.objects.filter(doctor=doctor).count()

        context = {
            'page_title': f'Doctor Dashboard - {request.user.first_name or request.user.username}',
            'active_page': 'dashboard',
            'role': 'doctor',
            'role_display': 'Doctor',
            'profile': profile,
            'prediction_history': prediction_history,
            'insights': insights,
            'doctor_name': request.user.first_name or request.user.username,
            'doctor': doctor,
            'prediction_results': prediction_results,
            'prediction_count': prediction_count,
        }
    elif user_role == 'hospital':
        hospital = getattr(request.user, 'hospital', None)
        if hospital is None:
            hospital = Hospital.objects.filter(user=request.user).first()

        total_doctors = hospital.doctors.count() if hospital else 0
        total_datasets = hospital.datasets.count() if hospital else 0
        doctors = hospital.doctors.all() if hospital else Doctor.objects.none()

        context = {
            'page_title': f'Hospital Dashboard - {request.user.first_name or request.user.username}',
            'active_page': 'dashboard',
            'role': 'hospital',
            'role_display': 'Hospital Admin',
            'profile': profile,
            'hospital_name': hospital.name if hospital else (request.user.first_name or request.user.username),
            'hospital': hospital,
            'total_doctors': total_doctors,
            'total_datasets': total_datasets,
            'doctors': doctors,
        }
    else:
        context = {
            'page_title': 'Dashboard - HeartFL',
            'active_page': 'dashboard',
            'role': 'user',
            'role_display': 'User',
            'profile': profile,
            'prediction_history': prediction_history,
            'insights': insights,
        }
    
    return render(request, 'accounts/dashboard.html', context)


def register_choice(request):
    """Registration choice page - Hospital or Doctor"""
    context = {
        'page_title': 'Register - HeartFL',
        'active_page': 'register'
    }
    return render(request, 'accounts/register_choice.html', context)


def hospital_register(request):
    """Hospital registration"""
    if request.method == 'POST':
        form = HospitalRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Hospital registered successfully! You can now login.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HospitalRegistrationForm()
    
    context = {
        'page_title': 'Hospital Registration - HeartFL',
        'active_page': 'register',
        'form': form,
        'register_type': 'hospital'
    }
    return render(request, 'accounts/hospital_register.html', context)


def doctor_register(request):
    """
    Doctor registration - must select a registered hospital.
    """
    # Check if any hospitals exist
    hospitals_count = Hospital.objects.count()
    
    if hospitals_count == 0:
        messages.warning(request, 'No hospitals registered yet. Please register a hospital first.')
        return redirect('accounts:hospital_register')
    
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Doctor registration successful! You can now login.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorRegistrationForm()
    
    context = {
        'page_title': 'Doctor Registration - HeartFL',
        'active_page': 'register',
        'form': form,
        'register_type': 'doctor'
    }
    return render(request, 'accounts/doctor_register.html', context)


def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')


@login_required
def user_settings(request):
    """
    User theme settings page - customize Dark & Light mode colors
    """
    # Get or create theme settings for user
    theme_settings, created = UserThemeSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ThemeSettingsForm(request.POST, instance=theme_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Theme settings updated successfully!')
            
            # Get user role for context
            user_role = request.session.get('user_role', 'user')
            profile = getattr(request.user, 'profile', None)
            if profile and profile.user_type:
                user_role = profile.user_type
            
            return redirect('accounts:settings')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ThemeSettingsForm(instance=theme_settings)
    
    # Get user role for context
    user_role = request.session.get('user_role', 'user')
    profile = getattr(request.user, 'profile', None)
    if profile and profile.user_type:
        user_role = profile.user_type
    
    context = {
        'page_title': 'Settings - HeartFL',
        'active_page': 'settings',
        'form': form,
        'theme_settings': theme_settings,
        'user_role': user_role,
        'role_display': 'Doctor' if user_role == 'doctor' else ('Hospital Admin' if user_role == 'hospital' else 'User'),
    }
    
    return render(request, 'accounts/settings.html', context)
