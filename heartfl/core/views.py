"""
Core App Views - Django Template Views
"""
import json

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from core.models import ContactMessage
from hospitals.models import Doctor, Hospital
from prediction.models import PredictionResult


def is_staff_or_superuser(user):
    """Check if user is staff or superuser"""
    return user.is_staff or user.is_superuser


def home(request):
    """Homepage with dashboard statistics."""
    hospitals_count = Hospital.objects.count()
    doctors_count = Doctor.objects.count()
    predictions_count = PredictionResult.objects.count()
    
    recent_predictions = (
        PredictionResult.objects.select_related('patient_data', 'doctor')
        .order_by('-predicted_at')[:10]
    )
    
    return render(
        request,
        'core/home.html',
        {
            'page_title': 'HeartFL - Heart Disease Prediction',
            'active_page': 'home',
            'hospitals_count': hospitals_count,
            'doctors_count': doctors_count,
            'predictions_count': predictions_count,
            'recent_predictions': recent_predictions,
        },
    )


def about(request):
    """About page with project information."""
    return render(
        request,
        'core/about.html',
        {
            'page_title': 'About - HeartFL',
            'active_page': 'about',
        },
    )


def demo_background(request):
    """Demo page showing heartbeat background with theme switching."""
    return render(
        request,
        'demo_background.html',
        {
            'page_title': 'Heartbeat Background Demo - HeartFL',
        },
    )


def contact_page(request):
    """Contact page with form."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()
        
        if not all([name, email, subject, message_text]):
            messages.error(request, 'All fields are required.')
        else:
            try:
                contact_msg = ContactMessage(
                    name=name,
                    email=email,
                    phone=phone,
                    subject=subject,
                    message=message_text,
                )
                contact_msg.save()
                messages.success(request, 'Thank you! Your message has been sent successfully.')
                return redirect('core:contact')
            except Exception as e:
                messages.error(request, f'Error sending message: {str(e)}')
    
    return render(
        request,
        'core/contact.html',
        {
            'page_title': 'Contact - HeartFL',
            'active_page': 'contact',
        },
    )


@require_http_methods(['GET'])
def overview_api(request):
    """Return high-level live stats for React dashboard."""
    total_hospitals = Hospital.objects.count()
    total_doctors = Doctor.objects.count()
    total_predictions = PredictionResult.objects.count()
    high_risk = PredictionResult.objects.filter(prediction='high').count()
    low_risk = PredictionResult.objects.filter(prediction='low').count()

    return JsonResponse(
        {
            'ok': True,
            'stats': {
                'total_hospitals': total_hospitals,
                'total_doctors': total_doctors,
                'total_predictions': total_predictions,
                'high_risk': high_risk,
                'low_risk': low_risk,
            },
        }
    )


@require_http_methods(['GET'])
def recent_predictions_api(request):
    """Return recent prediction rows for React tables/cards."""
    rows = []
    predictions = (
        PredictionResult.objects.select_related('patient_data', 'doctor')
        .order_by('-predicted_at')[:12]
    )

    for item in predictions:
        patient = item.patient_data
        rows.append(
            {
                'id': item.id,
                'patient_name': patient.patient_name,
                'age': patient.age,
                'gender': patient.gender,
                'doctor': item.doctor.full_name,
                'risk': item.prediction,
                'probability': round(float(item.probability), 2),
                'predicted_at': item.predicted_at.strftime('%Y-%m-%d %H:%M'),
            }
        )

    return JsonResponse({'ok': True, 'rows': rows})


@csrf_exempt
@require_http_methods(['POST'])
def contact_api(request):
    """API endpoint consumed by React contact form."""
    try:
        payload = json.loads(request.body.decode('utf-8')) if request.body else request.POST

        name = (payload.get('name') or '').strip()
        email = (payload.get('email') or '').strip()
        subject = (payload.get('subject') or '').strip()
        message = (payload.get('message') or '').strip()

        if not all([name, email, subject, message]):
            return JsonResponse(
                {'ok': False, 'message': 'All fields are required.'},
                status=400,
            )

        contact_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )
        contact_msg.save()

        return JsonResponse({'ok': True, 'message': 'Message submitted successfully.'})

    except Exception as exc:
        return JsonResponse(
            {'ok': False, 'message': f'Unable to submit message: {exc}'},
            status=500,
        )


# ============================================================================
# ADMIN VIEWS FOR CONTACT MESSAGES
# ============================================================================

@login_required
@user_passes_test(is_staff_or_superuser)
def contact_messages_admin(request):
    """Admin view to list all contact messages"""
    filter_type = request.GET.get('filter', 'all')
    
    if filter_type == 'unread':
        messages_list = ContactMessage.objects.filter(is_read=False).order_by('-submitted_at')
    elif filter_type == 'read':
        messages_list = ContactMessage.objects.filter(is_read=True).order_by('-submitted_at')
    else:
        messages_list = ContactMessage.objects.all().order_by('-submitted_at')
    
    total_messages = ContactMessage.objects.count()
    unread_count = ContactMessage.objects.filter(is_read=False).count()
    
    return render(request, 'admin/contact_messages.html', {
        'messages_list': messages_list,
        'total_messages': total_messages,
        'unread_count': unread_count,
        'filter': filter_type,
        'page_title': 'Contact Messages - Admin',
    })


@login_required
@user_passes_test(is_staff_or_superuser)
def view_contact_message_admin(request, message_id):
    """Admin view to see a single contact message"""
    try:
        message = ContactMessage.objects.get(id=message_id)
    except ContactMessage.DoesNotExist:
        messages.error(request, 'Message not found.')
        return redirect('core:contact_messages')
    
    return render(request, 'admin/view_contact_message.html', {
        'message': message,
        'page_title': f'Message from {message.name}',
    })


@login_required
@user_passes_test(is_staff_or_superuser)
def mark_message_as_read(request, message_id):
    """Mark a contact message as read"""
    try:
        message = ContactMessage.objects.get(id=message_id)
        message.is_read = True
        message.save()
        messages.success(request, 'Message marked as read.')
    except ContactMessage.DoesNotExist:
        messages.error(request, 'Message not found.')
    
    return redirect('core:view_contact_message', message_id=message_id)


@login_required
@user_passes_test(is_staff_or_superuser)
def delete_contact_message(request, message_id):
    """Delete a contact message"""
    try:
        message = ContactMessage.objects.get(id=message_id)
        message.delete()
        messages.success(request, 'Message deleted successfully.')
    except ContactMessage.DoesNotExist:
        messages.error(request, 'Message not found.')
    
    return redirect('core:contact_messages')
