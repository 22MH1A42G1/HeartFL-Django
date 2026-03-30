"""
Prediction App URLs
"""
from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    path('', views.predict, name='predict'),
    path('upload-pdf/', views.upload_pdf_and_extract, name='upload_pdf_extract'),
    path('predict-ajax/', views.predict_heart_disease, name='predict_ajax'),
    path('history/', views.prediction_history, name='history'),
    path('download-report/<int:prediction_id>/', views.download_prediction_report, name='download_report'),
]
