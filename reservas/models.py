from django.db import models
from django.contrib.auth.models import User

# Nota: Django ya trae una tabla 'User'. Usaremos esa para evitar crear 'Usuario' y 'Tipo_Usuario' manualmente.

class TipoServicio(models.Model):
    descripcion = models.CharField(max_length=255)
    def __str__(self): return self.descripcion

class Servicio(models.Model):
    nombre = models.CharField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.CASCADE)

class Habitacion(models.Model):
    tipo = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)
    capacidad = models.IntegerField()
    numero_hab = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='habitaciones/', null=True, blank=True)
    def __str__(self): return f"Hab {self.numero_hab} - {self.tipo}"

class Reserva(models.Model):
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    fecha_ingreso = models.DateField()
    fecha_salida = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE)
    servicios = models.ManyToManyField(Servicio) # Esto crea la tabla intermedia Reserva_Servicio automáticamente

class Pago(models.Model):
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    tipo_pago = models.CharField(max_length=100) # Simplificado para el alcance inicial

class Comprobante(models.Model):
    descripcion = models.CharField(max_length=255)
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)

class Resena(models.Model):
    comentario = models.CharField(max_length=255)
    valoracion = models.IntegerField()
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)