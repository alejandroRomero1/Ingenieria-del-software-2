from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .repositories import ReservaRepository
from .models import Habitacion
from datetime import datetime
import mercadopago
from django.conf import settings
from django.contrib import messages

def index(request):
    fecha_inicio = request.GET.get('inicio')
    fecha_fin = request.GET.get('fin')
    habitaciones = None

    if fecha_inicio and fecha_fin:
        # Validación defensiva de fechas
        if fecha_inicio >= fecha_fin:
            messages.error(request, "La fecha de salida debe ser posterior a la fecha de ingreso (mínimo 1 noche de estadía).")
            habitaciones = []  # No mostramos nada
        else:
            # Si el rango es correcto, buscamos en el repositorio
            habitaciones = ReservaRepository.buscar_habitaciones_disponibles(fecha_inicio, fecha_fin)
    else:
        # Al inicio, mostramos las habitaciones que no estén en mantenimiento
        habitaciones = ReservaRepository.obtener_todas_las_habitaciones().exclude(estado='Mantenimiento')
    
    return render(request, 'reservas/index.html', {
        'habitaciones': habitaciones,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    })

@login_required
def confirmar_reserva(request, habitacion_id):
    #  Obtenemos los datos básicos
    habitacion = Habitacion.objects.get(id=habitacion_id)
    fecha_inicio_str = request.GET.get('inicio')
    fecha_fin_str = request.GET.get('fin')
    
    # Cálculo de estadía
    # datetime.strptime convierte en tipo manejable para calcular la estadia.
    d1 = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
    d2 = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
    dias = (d2 - d1).days
    #aplicamos una regla de negocio para que no nos de 0 porque si elijen salir el mismo dia que entra dara 0.
    #si los dias son 0 asignamos el 1 .
    if dias <= 0: dias = 1
    
    precio_total = float(habitacion.precio * dias)

    # CONSTRUIMOS EL LINK A NUESTRO SIMULADOR 
    # Importante: Esto lleva a la URL que crearemos 
    init_point = f"/pasarela-simulada/?habitacion_id={habitacion_id}&inicio={fecha_inicio_str}&fin={fecha_fin_str}&precio={precio_total}"
            
    return render(request, 'reservas/confirmar.html', {
        'habitacion': habitacion,
        'inicio': fecha_inicio_str,
        'fin': fecha_fin_str,
        'dias': dias,
        'precio_total': precio_total,
        'init_point': init_point
    })

def exito(request):
    hab_id = request.GET.get('habitacion_id')   
    inicio = request.GET.get('inicio')
    fin = request.GET.get('fin')
    
    # CONTROL DE CONCURRENCIA: Doble chequeo antes de impactar la base de datos
    # Verificamos si en el último segundo otra persona le pisó las fechas
    habitaciones_libres = ReservaRepository.buscar_habitaciones_disponibles(inicio, fin)
    habitacion = Habitacion.objects.get(id=hab_id)

    if habitacion not in habitaciones_libres:
        # Si ya no está libre, frenamos el proceso y avisamos
        messages.error(request, "Lo sentimos, esta habitación fue reservada por otro usuario mientras procesabas el pago.")
        return redirect('/') # O la ruta de tu buscador principal

    # Si pasa el control, procedemos como siempre con el Observer
    total_calculado = ReservaRepository.calcular_total_reserva(inicio, fin, habitacion.precio)
    
    ReservaRepository.crear_reserva(
        usuario=request.user,
        habitacion_id=hab_id,
        f_ingreso=inicio,
        f_salida=fin,
        total=total_calculado  
    )
    
    return render(request, 'reservas/exito.html')

#def exito(request):
 #   # Recogemos los datos 
  #  hab_id = request.GET.get('habitacion_id')   
   # inicio = request.GET.get('inicio')
   # fin = request.GET.get('fin')
    
   # # Grabamos la reserva REAL en la DB
   # ReservaRepository.crear_reserva(
    #    usuario=request.user,
     #   habitacion_id=hab_id,
      #  f_ingreso=inicio,
       # f_salida=fin
   # )
    
    #return render(request, 'reservas/exito.html')



def pasarela_simulada(request):
    # Recibimos los datos por GET para pasarlos al final del proceso, datos que vienen en el init.
    hab_id = request.GET.get('habitacion_id')
    inicio = request.GET.get('inicio')
    fin = request.GET.get('fin')
    precio = request.GET.get('precio')
#Renderizamos la interfaz de la pasarela enviando estos datos
    return render(request, 'reservas/pasarela_simulada.html', {
        'hab_id': hab_id,
        'inicio': inicio,
        'fin': fin,
        'precio': precio
    })

def registrar_habitacion_view(request):
    """Vista que maneja la pantalla y el guardado de una nueva habitación"""
    if request.method == 'POST':
        # Capturamos los datos del formulario HTML
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')
        
        # CORRECCIÓN AQUÍ: Cambiamos 'capacidad' por 'capacity' para que coincida con tu HTML
        capacidad = request.POST.get('capacity') 
        
        numero_hab = request.POST.get('numero_hab')
        precio = request.POST.get('precio')
        estado = request.POST.get('estado')
        imagen = request.FILES.get('imagen')

        try:
            # Llamamos al repositorio
            ReservaRepository.crear_nueva_habitacion(
                tipo=tipo,
                descripcion=descripcion,
                capacidad=capacidad,
                numero_hab=numero_hab,
                precio=precio,
                estado=estado,
                imagen=imagen
            )
            messages.success(request, "La habitación se registró con éxito.")
            return redirect('listado_habitaciones')

        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'admin_hotel/registrar.html', {'datos': request.POST})

    return render(request, 'admin_hotel/registrar.html')

def listado_habitaciones_view(request):
    """Vista propia para listar las habitaciones con diseño personalizado"""
    # Llamamos a tu método del repositorio
    habitaciones = ReservaRepository.listar_total_habitaciones()
    return render(request, 'admin_hotel/listado.html', {'habitaciones': habitaciones})

def modificar_habitacion_view(request, id):
    """Vista propia para cargar y procesar la modificación de una habitación"""
    # 1. Ejecutamos el primer método del repositorio para rellenar el formulario
    habitacion = ReservaRepository.obtener_datos_habitacion(id)
    if not habitacion:
        messages.error(request, "La habitación seleccionada no existe.")
        return redirect('listado_habitaciones')

    if request.method == 'POST':
        # Capturamos los nuevos datos ingresados
        tipo = request.POST.get('tipo')
        descripcion = request.POST.get('descripcion')
        capacidad = request.POST.get('capacity') # asi lo llamados en el html
        numero_hab = request.POST.get('numero_hab')
        precio = request.POST.get('precio')
        estado = request.POST.get('estado')
        imagen = request.FILES.get('imagen')

        try:
            # 2. Ejecutamos el segundo método para impactar los cambios
            ReservaRepository.actualizar_datos_habitacion(
                id_habitacion=id, tipo=tipo, descripcion=descripcion,
                capacidad=capacidad, numero_hab=numero_hab, precio=precio,
                estado=estado, imagen=imagen
            )
            # Mensaje que pusiste en la conversación y redirección al listado
            messages.success(request, "La habitación se modificó con éxito.")
            return redirect('listado_habitaciones')

        except ValueError as e:
            messages.error(request, str(e))
            # Si falla, volvemos a mostrar el formulario con el error

    return render(request, 'admin_hotel/modificar.html', {'habitacion': habitacion})