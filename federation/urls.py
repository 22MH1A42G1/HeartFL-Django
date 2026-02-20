from django.urls import path
from . import views

app_name = 'federation'
urlpatterns = [
    path('rounds/', views.round_list, name='rounds'),
    path('rounds/start/', views.start_round, name='start_round'),
    path('rounds/<int:pk>/', views.round_detail, name='round_detail'),
]
