from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reporte/', views.reporte, name='reporte'),  # Esta ruta debe manejar /reporte/
]
