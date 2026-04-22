from .models import Habitacion, Reserva, Servicio
from django.db.models import Q
from datetime import datetime

class ReservaRepository:
    
    @staticmethod
    def obtener_todas_las_habitaciones():
        # Traemos solo las disponibles para no mostrar habitaciones en reparación
        return Habitacion.objects.filter(estado='Disponible')

    @staticmethod
    def buscar_habitaciones_disponibles(fecha_inicio, fecha_fin):
        """
        Lógica de Ingeniería: Filtra habitaciones que NO tengan reservas 
        confirmadas en el rango de fechas seleccionado.
        """
        reservas_ocupadas = Reserva.objects.filter(
            Q(fecha_ingreso__lt=fecha_fin) & Q(fecha_salida__gt=fecha_inicio)
        ).values_list('habitacion_id', flat=True)
        
        return Habitacion.objects.exclude(id__in=reservas_ocupadas).filter(estado='Disponible')

    @staticmethod
    def crear_reserva(usuario, habitacion_id, f_ingreso, f_salida):
        """
        Calcula el total y guarda la reserva en PostgreSQL.
        """
        habitacion = Habitacion.objects.get(id=habitacion_id)
        
        # Convertimos las fechas de texto a objetos de fecha para restar
        d1 = datetime.strptime(f_ingreso, '%Y-%m-%d')
        d2 = datetime.strptime(f_salida, '%Y-%m-%d')
        cantidad_dias = (d2 - d1).days
        
        # Si el usuario reserva por menos de un día, cobramos al menos 1 día
        if cantidad_dias <= 0:
            cantidad_dias = 1
            
        total_calculado = habitacion.precio * cantidad_dias

        return Reserva.objects.create(
            usuario=usuario,
            habitacion=habitacion,
            fecha_ingreso=f_ingreso,
            fecha_salida=f_salida,
            total=total_calculado
        )

class ServicioRepository:
    @staticmethod
    def obtener_servicios_activos():
        return Servicio.objects.all()