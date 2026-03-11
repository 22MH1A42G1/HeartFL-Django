"""
Prediction App Views - MONGODB INTEGRATED
==========================================

MONGODB QUERIES:
- Doctor.objects(username=...) to get doctor
- PatientData.save() creates MongoDB document
- PredictionResult.save() stores prediction in MongoDB
- Queries use MongoEngine syntax
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .forms_mongodb import PatientDataForm
from prediction.documents import PatientData, PredictionResult
from hospitals.documents import Doctor
from .ml_model import HeartDiseasePredictor
import traceback
from datetime import datetime

# PDF generation imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO


@login_required
def predict(request):
    """
    Heart disease prediction page.
    
    WORKFLOW:
    1. Verify user is doctor (query MongoDB)
    2. Collect patient data via form
    3. Save PatientData document to MongoDB
    4. Run ML prediction
    5. Save PredictionResult document to MongoDB
    """
    # Get doctor from MongoDB
    doctor = Doctor.objects(username=request.user.username).first()
    
    if not doctor:
        messages.error(request, 'Doctor profile not found. Please register as a doctor.')
        return redirect('accounts:doctor_register')
    
    prediction_result = None
    
    if request.method == 'POST':
        form = PatientDataForm(request.POST)
        if form.is_valid():
            try:
                # Save patient data to MongoDB
                patient_data = PatientData(
                    age=form.cleaned_data['age'],
                    sex=form.cleaned_data['sex'],
                    chest_pain_type=form.cleaned_data['chest_pain_type'],
                    resting_bp=form.cleaned_data['resting_bp'],
                    cholesterol=form.cleaned_data['cholesterol'],
                    fasting_bs=form.cleaned_data['fasting_bs'],
                    resting_ecg=form.cleaned_data['resting_ecg'],
                    max_heart_rate=form.cleaned_data['max_heart_rate'],
                    exercise_angina=form.cleaned_data['exercise_angina'],
                    oldpeak=form.cleaned_data['oldpeak'],
                    st_slope=form.cleaned_data['st_slope'],
                    doctor=doctor,
                    hospital=doctor.hospital  # Link to doctor's hospital
                )
                patient_data.save()
                
                # Perform ML prediction
                predictor = HeartDiseasePredictor()
                feature_vector = patient_data.to_feature_vector()
                prediction_label, probability = predictor.predict_from_features(feature_vector)
                
                # Determine binary prediction (0 or 1)
                prediction = 1 if prediction_label == "High Risk" else 0
                
                # Save prediction result to MongoDB
                prediction_result = PredictionResult(
                    patient=patient_data,
                    prediction=prediction,
                    prediction_label=prediction_label,
                    probability=probability / 100.0,  # Convert to 0-1 range
                    confidence_score=probability,
                    doctor=doctor,
                    hospital=doctor.hospital
                )
                prediction_result.save()
                
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
    """
    View prediction history for logged-in doctor.
    
    MONGODB QUERY:
    - Filter PredictionResult by doctor reference
    - Order by most recent first
    """
    # Get doctor from MongoDB
    doctor = Doctor.objects(username=request.user.username).first()
    
    if not doctor:
        messages.error(request, 'Doctor profile not found.')
        return redirect('core:home')
    
    # Get all predictions by this doctor
    predictions = PredictionResult.objects(doctor=doctor).order_by('-created_at')
    
    context = {
        'page_title': 'Prediction History - HeartFL',
        'predictions': predictions,
        'total_predictions': predictions.count()
    }
    return render(request, 'prediction/history.html', context)


@login_required
def download_prediction_report(request, prediction_id):
    """
    Generate and download a PDF report for a specific prediction.
    
    WORKFLOW:
    1. Fetch prediction result from MongoDB by ID
    2. Verify the prediction belongs to the logged-in doctor
    3. Generate PDF with all prediction details
    4. Return PDF as downloadable HTTP response
    
    PDF STRUCTURE:
    - Header: Hospital and doctor information
    - Patient details: Demographics and clinical parameters
    - Prediction result: Risk level, probability, confidence
    - Footer: Timestamp and disclaimers
    """
    # Get doctor from MongoDB
    doctor = Doctor.objects(username=request.user.username).first()
    
    if not doctor:
        messages.error(request, 'Doctor profile not found.')
        return redirect('core:home')
    
    # Fetch the prediction result from MongoDB
    try:
        prediction = PredictionResult.objects.get(id=prediction_id)
    except PredictionResult.DoesNotExist:
        messages.error(request, 'Prediction not found.')
        return redirect('prediction:history')
    
    # Security check: Ensure the prediction belongs to this doctor
    if prediction.doctor.id != doctor.id:
        messages.error(request, 'Access denied. This prediction does not belong to you.')
        return redirect('prediction:history')
    
    # Create PDF in memory
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#202124'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#5f6368'),
        alignment=TA_LEFT
    )
    
    # 1. TITLE
    title = Paragraph("Heart Disease Prediction Report", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # 2. HOSPITAL AND DOCTOR INFORMATION
    elements.append(Paragraph("Hospital Information", heading_style))
    
    hospital_data = [
        ['Hospital Name:', prediction.hospital.name],
        ['Registration Number:', prediction.hospital.registration_number],
        ['Address:', f"{prediction.hospital.address}, {prediction.hospital.city}, {prediction.hospital.state}"],
        ['Contact:', prediction.hospital.contact_number],
    ]
    
    hospital_table = Table(hospital_data, colWidths=[2*inch, 4.5*inch])
    hospital_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#202124')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#5f6368')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(hospital_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Doctor information
    elements.append(Paragraph("Doctor Information", heading_style))
    
    doctor_data = [
        ['Doctor Name:', f"Dr. {prediction.doctor.name}"],
        ['Specialization:', prediction.doctor.specialization or 'General Physician'],
        ['License Number:', prediction.doctor.license_number],
    ]
    
    doctor_table = Table(doctor_data, colWidths=[2*inch, 4.5*inch])
    doctor_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#202124')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#5f6368')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(doctor_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # 3. PATIENT DETAILS
    elements.append(Paragraph("Patient Clinical Data", heading_style))
    
    patient = prediction.patient
    
    # Gender mapping
    gender_display = 'Male' if patient.sex == 1 else 'Female'
    
    # Chest pain type mapping
    chest_pain_types = ['Typical Angina', 'Atypical Angina', 'Non-anginal Pain', 'Asymptomatic']
    chest_pain_display = chest_pain_types[patient.chest_pain_type] if patient.chest_pain_type < len(chest_pain_types) else 'Unknown'
    
    patient_data = [
        ['Age:', f"{patient.age} years"],
        ['Gender:', gender_display],
        ['Chest Pain Type:', chest_pain_display],
        ['Resting Blood Pressure:', f"{patient.resting_bp} mm Hg"],
        ['Cholesterol:', f"{patient.cholesterol} mg/dl"],
        ['Fasting Blood Sugar:', 'Yes (>120 mg/dl)' if patient.fasting_bs == 1 else 'No (<120 mg/dl)'],
        ['Resting ECG:', f"Type {patient.resting_ecg}"],
        ['Max Heart Rate:', f"{patient.max_heart_rate} bpm"],
        ['Exercise Induced Angina:', 'Yes' if patient.exercise_angina == 1 else 'No'],
        ['ST Depression (Oldpeak):', f"{patient.oldpeak}"],
        ['ST Slope:', f"Type {patient.st_slope}"],
    ]
    
    patient_table = Table(patient_data, colWidths=[2.5*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#202124')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#5f6368')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e8eaed')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # 4. PREDICTION RESULT
    elements.append(Paragraph("Prediction Result", heading_style))
    
    # Determine risk color
    risk_color = colors.HexColor('#d32f2f') if prediction.prediction == 1 else colors.HexColor('#388e3c')
    
    result_data = [
        ['Risk Level:', prediction.prediction_label],
        ['Probability:', f"{prediction.probability * 100:.2f}%"],
        ['Confidence Score:', f"{prediction.confidence_score:.2f}%"],
        ['Model Version:', prediction.model_version],
        ['Prediction Date:', prediction.created_at.strftime('%B %d, %Y')],
        ['Prediction Time:', prediction.created_at.strftime('%I:%M %p')],
    ]
    
    result_table = Table(result_data, colWidths=[2.5*inch, 4*inch])
    result_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTSIZE', (1, 0), (1, 0), 14),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#202124')),
        ('TEXTCOLOR', (1, 0), (1, 0), risk_color),
        ('TEXTCOLOR', (1, 1), (1, -1), colors.HexColor('#5f6368')),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (1, 0), (1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e8eaed')),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
    ]))
    elements.append(result_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # 5. RECOMMENDATION
    recommendation_style = ParagraphStyle(
        'Recommendation',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#202124'),
        alignment=TA_LEFT,
        leftIndent=10,
        rightIndent=10,
        spaceAfter=10,
        leading=14
    )
    
    if prediction.prediction == 1:
        recommendation_text = """
        <b>High Risk Detection:</b><br/>
        The patient shows indicators of high heart disease risk. Immediate medical consultation 
        and further diagnostic tests are recommended. Consider lifestyle modifications and 
        potential medical intervention. This screening tool is not a substitute for professional 
        medical diagnosis.
        """
    else:
        recommendation_text = """
        <b>Low Risk Detection:</b><br/>
        The patient shows low indicators of heart disease risk. Continue with regular health 
        checkups and maintain a healthy lifestyle. Monitor cardiovascular health periodically. 
        This screening tool is not a substitute for professional medical diagnosis.
        """
    
    elements.append(Paragraph("Medical Recommendation", heading_style))
    elements.append(Paragraph(recommendation_text, recommendation_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # 6. FOOTER / DISCLAIMER
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#80868b'),
        alignment=TA_CENTER,
        leading=10
    )
    
    disclaimer = """
    <b>Disclaimer:</b> This report is generated using a machine learning model trained with 
    Federated Learning across multiple hospitals. The prediction is for screening purposes only 
    and should not be considered as a final diagnosis. Always consult with qualified healthcare 
    professionals for proper diagnosis and treatment.
    """
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(disclaimer, footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data from buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    # Create HTTP response with PDF
    response = HttpResponse(pdf_data, content_type='application/pdf')
    
    # Set filename for download
    filename = f"Heart_Disease_Report_{prediction.created_at.strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
