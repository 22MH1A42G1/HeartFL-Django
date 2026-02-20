from django.urls import path
from . import views

app_name = 'hospitals'
urlpatterns = [
    path('', views.hospital_list, name='list'),
    path('upload/', views.upload_dataset, name='upload'),
    path('<int:pk>/', views.hospital_detail, name='detail'),
]
