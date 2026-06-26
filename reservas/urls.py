from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('reservar/<int:habitacion_id>/', views.confirmar_reserva, name='confirmar_reserva'),
    path('exito/', views.exito, name='exito'),
    path('pasarela-simulada/', views.pasarela_simulada, name='pasarela_simulada'),
    path('admin-hotel/habitaciones/nueva/', views.registrar_habitacion_view, name='registrar_habitacion'),
    path('admin-hotel/habitaciones/', views.listado_habitaciones_view, name='listado_habitaciones'),
    path('admin-hotel/habitaciones/modificar/<int:id>/', views.modificar_habitacion_view, name='modificar_habitacion'),
]