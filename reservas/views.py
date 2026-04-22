from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .repositories import ReservaRepository
from .models import Habitacion
from datetime import datetime
import mercadopago
from django.conf import settings

# ---  VISTA INDEX (MANTENIDA) ---
def index(request):
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    
    if fecha_inicio and fecha_fin:
        habitaciones = ReservaRepository.buscar_habitaciones_disponibles(fecha_inicio, fecha_fin)
    else:
        # Usamos el método del repositorio que ya tenés
        habitaciones = ReservaRepository.obtener_todas_las_habitaciones().filter(estado='Disponible')
    
    return render(request, 'reservas/index.html', {
        'habitaciones': habitaciones,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    })

@login_required
def confirmar_reserva(request, habitacion_id):
    # 1. Obtenemos los datos básicos
    habitacion = Habitacion.objects.get(id=habitacion_id)
    fecha_inicio_str = request.GET.get('inicio')
    fecha_fin_str = request.GET.get('fin')
    
    # 2. Cálculo de estadía
    d1 = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
    d2 = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
    dias = (d2 - d1).days
    if dias <= 0: dias = 1
    
    precio_total = float(habitacion.precio * dias)

    # 3. CONSTRUIMOS EL LINK A NUESTRO SIMULADOR (Sin usar SDK)
    # Importante: Esto lleva a la URL que crearemos en el paso 2
    init_point = f"/pasarela-simulada/?habitacion_id={habitacion_id}&inicio={fecha_inicio_str}&fin={fecha_fin_str}&precio={precio_total}"
            
    return render(request, 'reservas/confirmar.html', {
        'habitacion': habitacion,
        'inicio': fecha_inicio_str,
        'fin': fecha_fin_str,
        'dias': dias,
        'precio_total': precio_total,
        'init_point': init_point
    })

# 4. AGREGÁ ESTA NUEVA VISTA AL FINAL DE TU VIEWS.PY
def pasarela_simulada(request):
    return render(request, 'reservas/pasarela_simulada.html', {
        'hab_id': request.GET.get('habitacion_id'),
        'inicio': request.GET.get('inicio'),
        'fin': request.GET.get('fin'),
        'precio': request.GET.get('precio')
    })

def exito(request):
    # Recogemos los datos que mandamos en la back_url
    hab_id = request.GET.get('habitacion_id')
    inicio = request.GET.get('inicio')
    fin = request.GET.get('fin')
    
    # Grabamos la reserva REAL en la DB
    ReservaRepository.crear_reserva(
        usuario=request.user,
        habitacion_id=hab_id,
        f_ingreso=inicio,
        f_salida=fin
    )
    
    return render(request, 'reservas/exito.html')

def pasarela_simulada(request):
    # Recibimos los datos por GET para pasarlos al final del proceso
    hab_id = request.GET.get('habitacion_id')
    inicio = request.GET.get('inicio')
    fin = request.GET.get('fin')
    precio = request.GET.get('precio')

    return render(request, 'reservas/pasarela_simulada.html', {
        'hab_id': hab_id,
        'inicio': inicio,
        'fin': fin,
        'precio': precio
    })