"""
Federated Learning App URLs
"""
from django.urls import path
from . import views

app_name = 'federated'

urlpatterns = [
    path('dashboard/', views.fl_dashboard, name='dashboard'),
    path('visualization/', views.fl_visualization, name='visualization'),
]
