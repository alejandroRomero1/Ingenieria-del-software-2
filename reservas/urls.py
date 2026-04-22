from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reservar/<int:habitacion_id>/', views.confirmar_reserva, name='confirmar_reserva'),
    path('exito/', views.exito, name='exito'),
    path('pasarela-simulada/', views.pasarela_simulada, name='pasarela_simulada'),
]