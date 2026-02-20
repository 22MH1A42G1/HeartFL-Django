"""
Core App URLs
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact_page, name='contact'),
    path('demo-background/', views.demo_background, name='demo_background'),

    # Admin Contact Message Management (custom dashboard, not Django admin)
    path('messages/', views.contact_messages_admin, name='contact_messages'),
    path('messages/<int:message_id>/', views.view_contact_message_admin, name='view_contact_message'),
    path('messages/<int:message_id>/mark-read/', views.mark_message_as_read, name='mark_as_read'),
    path('messages/<int:message_id>/delete/', views.delete_contact_message, name='delete_contact_message'),

    # API Endpoints
    path('api/overview/', views.overview_api, name='overview_api'),
    path('api/recent-predictions/', views.recent_predictions_api, name='recent_predictions_api'),
    path('api/contact/', views.contact_api, name='contact_api'),
]
