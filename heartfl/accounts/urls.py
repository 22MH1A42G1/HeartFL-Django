"""
Accounts App URLs
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('settings/', views.user_settings, name='settings'),
    path('register/', views.register_choice, name='register_choice'),
    path('register/hospital/', views.hospital_register, name='hospital_register'),
    path('register/doctor/', views.doctor_register, name='doctor_register'),
]
