from django.db import models
from django.contrib.auth.models import User
from django.db import models, connection

# Nota: Django ya trae una tabla 'User'. Usaremos esa para evitar crear 'Usuario' y 'Tipo_Usuario' manualmente.

class TipoServicio(models.Model):
    descripcion = models.CharField(max_length=255)
    def __str__(self): return self.descripcion

class Servicio(models.Model):
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.CASCADE)
    def __str__(self): return self.nombre

class Habitacion(models.Model):
    tipo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)
    capacidad = models.IntegerField()
    numero_hab = models.IntegerField(unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='habitaciones/', null=True, blank=True)

    def __str__(self): 
        return f"Hab {self.numero_hab} - {self.tipo}"

    @classmethod
    def buscar_habitaciones_disponibles(cls, fecha_inicio, fecha_fin):
        """
        Busca habitaciones libres ejecutando el PROCEDIMIENTO ALMACENADO
        optimizado directamente en PostgreSQL.
        """
        from django.db.models.fields.files import ImageFieldFile

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM obtener_habitaciones_disponibles(%s, %s);", 
                [fecha_inicio, fecha_fin]
            )
            
            columnas = [col[0] for col in cursor.description]
            resultados_raw = cursor.fetchall()
            
            resultados = []
            for fila in resultados_raw:
                dicc = dict(zip(columnas, fila))
                
                if dicc['imagen']:
                    instancia_temp = cls(id=dicc['id'])
                    dicc['imagen'] = ImageFieldFile(instancia_temp, cls._meta.get_field('imagen'), dicc['imagen'])
                
                resultados.append(dicc)
            
        return resultados

    # === ACÁ QUEDA AGREGADO EL NUEVO MÉTODO PARA EL SEGUNDO PROCEDIMIENTO ===
    @classmethod
    def actualizar_datos_habitacion(cls, id_habitacion, tipo, descripcion, capacidad, numero_hab, precio, estado):
        """
        Ejecuta el Procedimiento Almacenado de ACTUALIZACIÓN completa
        directamente en PostgreSQL utilizando la sentencia CALL.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                "CALL actualizar_datos_habitacion(%s, %s, %s, %s, %s, %s, %s);",
                [id_habitacion, tipo, descripcion, capacidad, numero_hab, precio, estado]
            )
        return True 

class Reserva(models.Model):
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    servicios = models.ManyToManyField(Servicio) # Tabla intermedia automática

    # =========================================================================
    # LÓGICA E INFRAESTRUCTURA DEL PATRÓN OBSERVER 
    # =========================================================================
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializamos la lista de observadores en memoria
        self._observers = []
        self._registrar_observadores_por_defecto()

    def _registrar_observadores_por_defecto(self):
        """Registra automáticamente los 4 observadores de tu diagrama"""
        from .observers import HabitacionObserver, EmailObserver, ComprobanteObserver, PagoObserver
        self.agregarObserver(HabitacionObserver())
        self.agregarObserver(EmailObserver())
        self.agregarObserver(ComprobanteObserver())
        self.agregarObserver(PagoObserver())

    def agregarObserver(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def eliminarObserver(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notificarObservers(self):
        """Recorre cada observador y ejecuta su acción secundaria"""
        for observer in self._observers:
            observer.actualizar(self)

    def confirmar_reserva(self):
        """
        Método clave del diagrama. Cuando se confirma la reserva,
        gatilla de forma automática la notificación a todo el ecosistema.
        """
        # Guardamos la reserva en la base de datos
        self.save()
        
        # ¡se dispara el patrón!
        self.notificarObservers()

    def __str__(self):
        return f"Reserva {self.id} - Hab {self.habitacion.numero_hab} ({self.usuario.username})"


class Pago(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    tipo_pago = models.CharField(max_length=100) 

class Comprobante(models.Model):
    descripcion = models.CharField(max_length=255)
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)

class Resena(models.Model):
    comentario = models.CharField(max_length=255)
    valoracion = models.IntegerField()
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)