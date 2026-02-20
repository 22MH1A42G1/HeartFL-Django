"""
Prediction App URLs
"""
from django.urls import path
from . import views

app_name = 'prediction'

urlpatterns = [
    path('', views.predict, name='predict'),
    path('history/', views.prediction_history, name='history'),
    path('download-report/<int:prediction_id>/', views.download_prediction_report, name='download_report'),
]
