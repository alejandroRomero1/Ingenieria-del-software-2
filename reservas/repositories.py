from .models import Habitacion, Reserva, Servicio
from django.db.models import Q
from datetime import datetime

class ReservaRepository:

    @staticmethod
    def obtener_datos_habitacion(id_habitacion):
        """Trae una habitación específica por su ID para el formulario"""
        from .models import Habitacion
        try:
            return Habitacion.objects.get(id=id_habitacion)
        except Habitacion.DoesNotExist:
            return None

    @staticmethod
    def actualizar_datos_habitacion(id_habitacion, tipo, descripcion, capacidad, numero_hab, precio, estado, imagen=None):
        """
        Actualiza los datos de la habitación utilizando el Procedimiento Almacenado
        y maneja la imagen de forma complementaria.
        """
        from .models import Habitacion
        
        # 1. Ejecutamos el procedimiento almacenado en Postgres para impactar los textos y números
        Habitacion.actualizar_datos_habitacion(
            id_habitacion=id_habitacion,
            tipo=tipo,
            descripcion=descripcion,
            capacidad=int(capacidad),
            numero_hab=int(numero_hab),
            precio=precio,
            estado=estado
        )
        
        # 2. Si el usuario subió una imagen nueva, dejamos que Django la guarde de forma nativa en su carpeta media/
        if imagen:
            habitacion_obj = Habitacion.objects.get(id=id_habitacion)
            habitacion_obj.imagen = imagen
            habitacion_obj.save(update_fields=['imagen'])
            
        return True
    
    @staticmethod
    
    def listar_total_habitaciones():
        """Trae todas las habitaciones de la base de datos para nuestro listado propio"""
        from .models import Habitacion
        return Habitacion.objects.all().order_by('numero_hab')

    @staticmethod
    def crear_nueva_habitacion(tipo, descripcion, capacidad, numero_hab, precio, estado, imagen):
        """
        Este método mapea directamente el Paso 4.1 del caso de uso 'Registrar habitación'.
        Recibe los datos del formulario e intenta impactar en la base de datos.
        """
        from .models import Habitacion  # Aseguramos la importación del modelo

        # 1. CURSO ALTERNATIVO: Validamos si el número de habitación ya existe
        if Habitacion.objects.filter(numero_hab=numero_hab).exists():
            # Si existe, lanzamos un error (para que la vista lo capture y muestre el mensaje de error)
            raise ValueError("Habitación con este Número Hab ya existe.")
        
        # 2. CURSO NORMAL: Si no está duplicado, creamos el registro de forma persistente
        nueva_hab = Habitacion.objects.create(
            tipo=tipo,
            descripcion=descripcion,
            capacidad=capacidad,
            numero_hab=numero_hab,
            precio=precio,
            estado=estado,
            imagen=imagen
        )
        
        return nueva_hab
    
    
    @staticmethod
    def obtener_todas_las_habitaciones():
        # Traemos solo las disponibles para no mostrar habitaciones en reparación
        return Habitacion.objects.filter(estado='Disponible')

    #@staticmethod
    #def buscar_habitaciones_disponibles(fecha_inicio, fecha_fin):
    #    """
    #    Busca habitaciones libres mapeando correctamente las fechas 
    #    e ignorando el estado 'Ocupada' de reservas previas ya finalizadas.
    #    """
    #    from .models import Reserva, Habitacion
    #    from django.db.models import Q

    #    # 1. Buscamos los IDs de habitaciones que SÍ tienen reservas superpuestas en este rango
    #    reservas_ocupadas = Reserva.objects.filter(
    #        Q(fecha_ingreso__lt=fecha_fin) & Q(fecha_salida__gt=fecha_inicio)
    #    ).values_list('habitacion_id', flat=True)

    #    # 2. Traemos todas las habitaciones EXCLUYENDO las reservadas en esa fecha
    #    # y EXCLUYENDO únicamente las que estén en mantenimiento físico.
    #    return Habitacion.objects.exclude(id__in=reservas_ocupadas).exclude(estado='Mantenimiento')
    
    @staticmethod
    def buscar_habitaciones_disponibles(fecha_inicio, fecha_fin):
        """
        Busca habitaciones libres delegando la consulta al método del modelo
        que ejecuta el procedimiento almacenado.
        """
        from .models import Habitacion
        
        # Llamamos al método del modelo con su nombre limpio y documentado
        return Habitacion.buscar_habitaciones_disponibles(fecha_inicio, fecha_fin)

    @staticmethod
    def calcular_total_reserva(f_ingreso, f_salida, precio_noche):
        d1 = datetime.strptime(f_ingreso, '%Y-%m-%d')
        d2 = datetime.strptime(f_salida, '%Y-%m-%d')
        cantidad_dias = (d2 - d1).days
        
        if cantidad_dias <= 0:
            cantidad_dias = 1
            
        return precio_noche * cantidad_dias


    @staticmethod
    def crear_reserva(usuario, habitacion_id, f_ingreso, f_salida, total):
        from .models import Reserva
        
        # Instanciamos el objeto en memoria (el Sujeto)
        nueva_reserva = Reserva(
            usuario=usuario,
            habitacion_id=habitacion_id,
            fecha_ingreso=f_ingreso,
            fecha_salida=f_salida,
            total=total
        )
        
        # ¡método clave que guarda e invoca a los observadores!
        nueva_reserva.confirmar_reserva()
        return nueva_reserva

    

class ServicioRepository:
    @staticmethod
    def obtener_servicios_activos():
        return Servicio.objects.all()


    