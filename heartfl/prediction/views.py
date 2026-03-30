"""
Prediction App Views
Heart disease prediction and patient data management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.urls import reverse
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
import json
import re
from io import BytesIO

from hospitals.models import Hospital

logger = logging.getLogger(__name__)


def _extract_first_int(patterns, text, default=None):
    """Extract the first integer matching one of the provided regex patterns."""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except (TypeError, ValueError):
                continue
    return default


def _extract_first_float(patterns, text, default=None):
    """Extract the first float matching one of the provided regex patterns."""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except (TypeError, ValueError):
                continue
    return default


def _extract_pdf_text(pdf_bytes):
    """Extract text from PDF using embedded text first, then OCR fallback per page."""
    try:
        import fitz
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError('OCR dependencies are missing. Install pytesseract and PyMuPDF.') from exc

    document = fitz.open(stream=pdf_bytes, filetype='pdf')
    page_text_chunks = []

    for page in document:
        text = page.get_text('text') or ''
        text = text.strip()
        if text:
            page_text_chunks.append(text)
            continue

        # OCR fallback for scanned PDFs where embedded text is unavailable.
        pix = page.get_pixmap(dpi=300)
        image = Image.open(BytesIO(pix.tobytes('png')))
        ocr_text = pytesseract.image_to_string(image) or ''
        page_text_chunks.append(ocr_text)

    document.close()
    joined_text = '\n'.join(page_text_chunks)
    return re.sub(r'\s+', ' ', joined_text).strip()


def _parse_clinical_data_from_text(text):
    """Parse OCR text into structured prediction features expected by the UI/model."""
    normalized = text.lower()

    age = _extract_first_int([r'age\s*[:\-]?\s*(\d{1,3})'], text)
    resting_bp = _extract_first_int([
        r'(?:resting\s*(?:blood\s*pressure|bp)|blood\s*pressure|bp)\s*[:\-]?\s*(\d{2,3})'
    ], text)
    cholesterol = _extract_first_int([
        r'(?:cholesterol|chol)\s*[:\-]?\s*(\d{2,4})'
    ], text)
    max_heart_rate = _extract_first_int([
        r'(?:max(?:imum)?\s*heart\s*rate|heart\s*rate|hr)\s*[:\-]?\s*(\d{2,3})'
    ], text)
    oldpeak = _extract_first_float([
        r'(?:oldpeak|st\s*depression)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?)'
    ], text)

    sex = None
    if re.search(r'\bsex\s*[:\-]?\s*male\b|\bgender\s*[:\-]?\s*male\b|\bmale\b', normalized):
        sex = 'Male'
    elif re.search(r'\bsex\s*[:\-]?\s*female\b|\bgender\s*[:\-]?\s*female\b|\bfemale\b', normalized):
        sex = 'Female'

    chest_pain_type = None
    if re.search(r'typical\s*angina', normalized):
        chest_pain_type = 0
    elif re.search(r'atypical\s*angina', normalized):
        chest_pain_type = 1
    elif re.search(r'non[-\s]?anginal', normalized):
        chest_pain_type = 2
    elif re.search(r'asymptomatic', normalized):
        chest_pain_type = 3
    else:
        chest_pain_type = _extract_first_int([
            r'(?:chest\s*pain\s*type|cp)\s*[:\-]?\s*([0-3])'
        ], text)

    fasting_bs = None
    if re.search(r'fasting\s*(?:blood\s*sugar|bs)[^\.]{0,30}(?:yes|positive|true|>\s*120)', normalized):
        fasting_bs = 'Yes'
    elif re.search(r'fasting\s*(?:blood\s*sugar|bs)[^\.]{0,30}(?:no|negative|false|<=\s*120)', normalized):
        fasting_bs = 'No'

    resting_ecg = None
    if re.search(r'left\s*ventricular\s*hypertrophy', normalized):
        resting_ecg = 2
    elif re.search(r'st[-\s]*t\s*wave\s*abnormal', normalized):
        resting_ecg = 1
    elif re.search(r'\bnormal\s*ecg\b|resting\s*ecg\s*[:\-]?\s*normal', normalized):
        resting_ecg = 0
    else:
        resting_ecg = _extract_first_int([
            r'(?:rest(?:ing)?\s*ecg|ecg)\s*[:\-]?\s*([0-2])'
        ], text)

    exercise_angina = None
    if re.search(r'exercise\s*induced\s*angina[^\.]{0,20}(?:yes|positive|true)', normalized):
        exercise_angina = 'Yes'
    elif re.search(r'exercise\s*induced\s*angina[^\.]{0,20}(?:no|negative|false)', normalized):
        exercise_angina = 'No'

    st_slope = None
    if re.search(r'\bupsloping\b', normalized):
        st_slope = 0
    elif re.search(r'\bflat\b', normalized):
        st_slope = 1
    elif re.search(r'\bdownsloping\b', normalized):
        st_slope = 2
    else:
        st_slope = _extract_first_int([
            r'(?:st\s*slope|slope)\s*[:\-]?\s*([0-2])'
        ], text)

    return {
        'age': age,
        'sex': sex,
        'chest_pain_type': chest_pain_type,
        'resting_bp': resting_bp,
        'cholesterol': cholesterol,
        'fasting_bs': fasting_bs,
        'resting_ecg': resting_ecg,
        'max_heart_rate': max_heart_rate,
        'exercise_angina': exercise_angina,
        'oldpeak': oldpeak,
        'st_slope': st_slope,
    }


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
@require_POST
def upload_pdf_and_extract(request):
    """Accept a PDF medical report, extract text and return parsed clinical JSON."""
    if not _is_doctor(request):
        return JsonResponse({'error': 'Access denied. Doctor account required.'}, status=403)

    uploaded_file = request.FILES.get('pdf_file')
    if not uploaded_file:
        return JsonResponse({'error': 'No PDF file provided.'}, status=400)

    if not uploaded_file.name.lower().endswith('.pdf'):
        return JsonResponse({'error': 'Invalid file type. Please upload a PDF.'}, status=400)

    try:
        pdf_bytes = uploaded_file.read()
        extracted_text = _extract_pdf_text(pdf_bytes)
        if not extracted_text:
            return JsonResponse({'error': 'Unable to extract text from PDF.'}, status=422)

        parsed_data = _parse_clinical_data_from_text(extracted_text)
        return JsonResponse({'data': parsed_data})
    except Exception as exc:
        logger.exception('PDF extraction failed: %s', exc)
        return JsonResponse({'error': 'OCR processing failed. Please try another PDF.'}, status=500)


def _parse_prediction_payload(request):
    """Support both JSON and form-encoded payloads for AJAX prediction."""
    if request.content_type and 'application/json' in request.content_type:
        try:
            return json.loads(request.body.decode('utf-8'))
        except (TypeError, ValueError, json.JSONDecodeError):
            return {}
    return request.POST


@login_required
@require_http_methods(['POST'])
def predict_heart_disease(request):
    """Predict heart disease risk from submitted clinical data and return JSON."""
    if not _is_doctor(request):
        return JsonResponse({'error': 'Access denied. Doctor account required.'}, status=403)

    payload = _parse_prediction_payload(request)

    def _required_value(key):
        value = payload.get(key)
        if value is None or str(value).strip() == '':
            raise ValueError(f'{key} is required')
        return value

    def _to_float(value):
        # Accept both decimal separators, e.g., 1.5 and 1,5
        return float(str(value).strip().replace(',', '.'))

    st_slope_map = {
        'upsloping': 0,
        'flat': 1,
        'downsloping': 2,
    }

    try:
        age = int(_required_value('age'))
        sex_value = str(_required_value('sex')).strip().lower()
        chest_pain_type = int(_required_value('chest_pain_type'))
        resting_bp = int(_required_value('resting_bp'))
        cholesterol = int(_required_value('cholesterol'))
        fasting_bs_raw = str(payload.get('fasting_bs', '')).strip().lower()
        resting_ecg = int(_required_value('resting_ecg'))
        max_heart_rate = int(_required_value('max_heart_rate'))
        exercise_angina_raw = str(payload.get('exercise_angina', '')).strip().lower()
        oldpeak = _to_float(_required_value('oldpeak'))

        st_slope_raw = str(_required_value('st_slope')).strip().lower()
        st_slope = st_slope_map.get(st_slope_raw, int(st_slope_raw))
    except (TypeError, ValueError) as exc:
        return JsonResponse({'error': f'Invalid input values. {str(exc)}'}, status=400)

    sex = 1 if sex_value in ('male', 'm', '1') else 0
    fasting_bs = 1 if fasting_bs_raw in ('yes', 'true', '1', 'on') else 0
    exercise_angina = 1 if exercise_angina_raw in ('yes', 'true', '1', 'on') else 0

    predictor = HeartDiseasePredictor()
    prediction_label, probability_percent = predictor.predict_from_features([
        age,
        sex,
        chest_pain_type,
        resting_bp,
        cholesterol,
        fasting_bs,
        resting_ecg,
        max_heart_rate,
        exercise_angina,
        oldpeak,
        st_slope,
    ])

    normalized_prediction = 'High Risk' if prediction_label.lower().startswith('high') else 'Low Risk'
    risk_color = 'danger' if normalized_prediction == 'High Risk' else 'success'

    # Persist the prediction so report download works for AJAX flow.
    doctor = _ensure_doctor_record(request.user)
    patient_name = str(payload.get('patient_name', '')).strip() or 'OCR Patient'
    gender = 'M' if sex == 1 else 'F'

    patient_data = PatientData.objects.create(
        doctor=doctor,
        patient_name=patient_name,
        age=age,
        gender=gender,
        chest_pain_type=chest_pain_type,
        resting_bp=resting_bp,
        cholesterol=cholesterol,
        fasting_bs=bool(fasting_bs),
        resting_ecg=resting_ecg,
        max_heart_rate=max_heart_rate,
        exercise_angina=bool(exercise_angina),
        oldpeak=oldpeak,
        st_slope=st_slope,
    )

    prediction_record = PredictionResult.objects.create(
        patient_data=patient_data,
        doctor=doctor,
        prediction='high' if normalized_prediction == 'High Risk' else 'low',
        probability=float(probability_percent),
        confidence_score=float(probability_percent),
    )

    report_url = reverse('prediction:download_report', args=[prediction_record.id])

    return JsonResponse({
        'prediction': normalized_prediction,
        'probability': round(probability_percent / 100.0, 4),
        'probability_percent': round(probability_percent, 2),
        'risk_color': risk_color,
        'prediction_id': prediction_record.id,
        'report_url': report_url,
    })


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
