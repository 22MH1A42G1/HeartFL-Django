from django.urls import path
from . import views

app_name = 'predictions'
urlpatterns = [
    path('', views.prediction_list, name='list'),
    path('new/', views.new_prediction, name='new'),
    path('<int:pk>/', views.prediction_detail, name='detail'),
]
