"""
Prediction App Views
Heart disease prediction and patient data management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms import PatientDataForm
from .models import PatientData, PredictionResult
from hospitals.models import Doctor
from .ml_model import HeartDiseasePredictor
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import traceback
import logging
from hospitals.models import Hospital

logger = logging.getLogger(__name__)


def _ensure_doctor_record(user):
    """Get or create a Doctor record for the user."""
    try:
        # If doctor already exists, return it
        if hasattr(user, 'doctor') and user.doctor:
            return user.doctor
        
        # Create Hospital record if needed
        hospital, _ = Hospital.objects.get_or_create(
            user=user,
            defaults={
                'name': f'{user.first_name or user.username}\'s Hospital',
                'address': 'Hospital Address',
                'city': 'City',
                'state': 'State',
                'pincode': '000000',
                'contact_number': '0000000000',
                'email': user.email or f'{user.username}@hospital.local',
                'registration_number': f'REG-{user.id}',
                'is_verified': True
            }
        )
        
        # Create Doctor record for the user
        doctor, created = Doctor.objects.get_or_create(
            user=user,
            defaults={
                'hospital': hospital,
                'full_name': user.first_name or user.username,
                'specialization': 'General Medicine',
                'license_number': f'LIC-{user.id}',
                'phone': '0000000000',
                'email': user.email or f'{user.username}@doctor.local',
                'is_active': True
            }
        )
        
        if created:
            logger.info('Auto-created Doctor record for user: %s', user.username)
        
        return doctor
    except Exception as exc:
        logger.error('Failed to ensure doctor record for %s: %s', user.username, exc)
        raise


def _is_doctor(request):
    """Check if user is a doctor (via Doctor model or session role from login)"""
    # Check Doctor model relationship (primary)
    if hasattr(request.user, 'doctor'):
        return True
    # Check session role set during login (fallback for test accounts)
    if request.session.get('user_role') == 'doctor':
        return True
    return False


@login_required
def predict(request):
    """Heart disease prediction page"""
    # Check if user is a doctor
    if not _is_doctor(request):
        messages.error(request, 'Access denied. Doctor account required.')
        return redirect('core:home')
    
    # Ensure doctor record exists
    doctor = _ensure_doctor_record(request.user)
    
    prediction_result = None
    
    if request.method == 'POST':
        form = PatientDataForm(request.POST)
        if form.is_valid():
            try:
                # Save patient data
                patient_data = form.save(commit=False)
                patient_data.doctor = doctor
                patient_data.save()
                
                # Perform prediction
                predictor = HeartDiseasePredictor()
                prediction, probability = predictor.predict(patient_data)
                
                # Save prediction result
                prediction_result = PredictionResult.objects.create(
                    patient_data=patient_data,
                    doctor=doctor,
                    prediction=prediction,
                    probability=probability,
                    confidence_score=probability
                )
                
                messages.success(request, 'Prediction completed successfully!')
                
            except Exception as e:
                messages.error(request, f'Prediction error: {str(e)}')
                traceback.print_exc()
    else:
        form = PatientDataForm()
    
    context = {
        'page_title': 'Heart Disease Prediction - HeartFL',
        'active_page': 'predict',
        'form': form,
        'prediction_result': prediction_result
    }
    return render(request, 'prediction/predict.html', context)


@login_required
def prediction_history(request):
    """View prediction history for logged-in doctor"""
    if not _is_doctor(request):
        messages.error(request, 'Access denied. Doctor account required.')
        return redirect('core:home')
    
    # Ensure doctor record exists
    doctor = _ensure_doctor_record(request.user)
    
    predictions = PredictionResult.objects.filter(doctor=doctor)
    
    context = {
        'page_title': 'Prediction History - HeartFL',
        'predictions': predictions,
        'total_predictions': predictions.count()
    }
    return render(request, 'prediction/history.html', context)


@login_required
def download_prediction_report(request, prediction_id):
    """
    Generate and download PDF report for a prediction result.
    Only accessible by the doctor who created the prediction.
    """
    # Check if user is a doctor
    if not _is_doctor(request):
        messages.error(request, 'Access denied.')
        return redirect('prediction:history')
    
    # Ensure doctor record exists
    doctor = _ensure_doctor_record(request.user)
    
    # Get prediction result
    prediction_result = get_object_or_404(PredictionResult, id=prediction_id)
    
    # Verify it matches the logged-in doctor
    if prediction_result.doctor != doctor:
        messages.error(request, 'Access denied.')
        return redirect('prediction:history')
    
    # Create HTTP response with PDF mime type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="heart_disease_report_{prediction_id}.pdf"'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Header
    elements.append(Paragraph("Heart Disease Prediction Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Hospital & Doctor Information
    doctor = prediction_result.doctor
    hospital_data = [
        ['Hospital:', doctor.hospital.name],
        ['Doctor:', f'Dr. {doctor.full_name}'],
        ['Specialization:', doctor.specialization or 'General Medicine'],
        ['License Number:', doctor.license_number],
        ['Report Date:', datetime.now().strftime('%B %d, %Y %I:%M %p')]
    ]
    
    hospital_table = Table(hospital_data, colWidths=[2*inch, 4*inch])
    hospital_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    
    elements.append(hospital_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Patient Information Section
    elements.append(Paragraph("Patient Information", heading_style))
    
    patient = prediction_result.patient_data
    gender_display = 'Male' if patient.gender == 'M' else 'Female'
    
    patient_data = [
        ['Patient Name:', patient.patient_name],
        ['Age:', f'{patient.age} years'],
        ['Gender:', gender_display],
        ['Record Date:', patient.created_at.strftime('%B %d, %Y')]
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    
    elements.append(patient_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Clinical Data Section
    elements.append(Paragraph("Clinical Data", heading_style))
    
    chest_pain_types = {0: 'Typical Angina', 1: 'Atypical Angina', 2: 'Non-anginal Pain', 3: 'Asymptomatic'}
    
    clinical_data = [
        ['Parameter', 'Value'],
        ['Chest Pain Type', chest_pain_types.get(patient.chest_pain_type, 'Unknown')],
        ['Resting Blood Pressure', f'{patient.resting_bp} mm Hg'],
        ['Cholesterol', f'{patient.cholesterol} mg/dl'],
        ['Fasting Blood Sugar', 'Yes (>120 mg/dl)' if patient.fasting_bs else 'No (<120 mg/dl)'],
        ['Resting ECG', str(patient.resting_ecg)],
        ['Max Heart Rate', f'{patient.max_heart_rate} bpm'],
        ['Exercise Induced Angina', 'Yes' if patient.exercise_angina else 'No'],
        ['ST Depression (Oldpeak)', f'{patient.oldpeak}'],
        ['ST Slope', str(patient.st_slope)]
    ]
    
    clinical_table = Table(clinical_data, colWidths=[3*inch, 3*inch])
    clinical_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    
    elements.append(clinical_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Prediction Results Section
    elements.append(Paragraph("Prediction Results", heading_style))
    
    # Determine risk color
    if prediction_result.prediction == 'high':
        risk_color = colors.HexColor('#e74c3c')
        risk_bg = colors.HexColor('#fadbd8')
        risk_text = 'HIGH RISK'
    else:
        risk_color = colors.HexColor('#27ae60')
        risk_bg = colors.HexColor('#d5f4e6')
        risk_text = 'LOW RISK'
    
    result_data = [
        ['Prediction', 'Probability'],
        [risk_text, f'{prediction_result.probability:.2f}%']
    ]
    
    result_table = Table(result_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BACKGROUND', (0, 1), (0, 1), risk_bg),
        ('TEXTCOLOR', (0, 1), (0, 1), risk_color),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (0, 1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#34495e'))
    ]))
    
    elements.append(result_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Notes Section
    if prediction_result.notes:
        elements.append(Paragraph("Doctor's Notes", heading_style))
        notes_style = ParagraphStyle(
            'Notes',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12
        )
        elements.append(Paragraph(prediction_result.notes, notes_style))
    
    # Footer
    elements.append(Spacer(1, 0.4*inch))
    footer_text = """
    <para align=center>
    <font size=8 color='#7f8c8d'>
    This report is generated by HeartFL - Federated Learning for Heart Disease Prediction<br/>
    Report ID: {}<br/>
    Generated on: {}<br/>
    <b>DISCLAIMER:</b> This prediction is for reference only. Please consult with a qualified healthcare provider for diagnosis and treatment.
    </font>
    </para>
    """.format(prediction_id, datetime.now().strftime('%B %d, %Y %I:%M %p'))
    
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    return response
