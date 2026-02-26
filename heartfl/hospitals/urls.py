"""
Hospital App URLs
"""
from django.urls import path
from . import views

app_name = 'hospitals'

urlpatterns = [
    path('dashboard/', views.hospital_dashboard, name='dashboard'),
    path('upload/', views.upload_dataset, name='upload_dataset'),
    path('dataset/<str:dataset_id>/', views.view_dataset, name='view_dataset'),
]
