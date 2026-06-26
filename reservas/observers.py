# reservas/observers.py
from abc import ABC, abstractmethod
from django.core.mail import send_mail


class Observer(ABC):
    @abstractmethod
    def actualizar(self, reserva):
        pass

class HabitacionObserver(Observer):
    def actualizar(self, reserva):
        """Modifica el estado de la habitación asignada de forma automática"""
        # Gracias a tu ForeignKey, llegamos directo a la habitación seleccionada
        habitacion = reserva.habitacion 
        if habitacion:
            habitacion.estado = 'Ocupada'
            habitacion.save()
            print(f"[Observer] ÉXITO: Habitación #{habitacion.numero_hab} pasó a 'Ocupada'.")

class EmailObserver:  
    def actualizar(self, reserva):
        usuario = reserva.usuario
        habitacion = reserva.habitacion
        
        correo_destino = usuario.email if (usuario and usuario.email) else "cliente_prueba@hotel.com"
        asunto = f"¡Tu reserva de la Habitación #{habitacion.numero_hab} está Confirmada! 🏨"
        
        cuerpo_mensaje = (
            f"Hola {usuario.username if usuario else 'Cliente'},\n\n"
            f"¡Tu pago fue procesado con éxito! Acá tenés el detalle de tu estadía:\n\n"
            f"📌 Código de Reserva: #{reserva.id if reserva.id else 'TEMP'}\n"
            f"🛏️ Habitación: {habitacion.numero_hab} ({habitacion.tipo})\n"
            f"📅 Ingreso (Check-In): {reserva.fecha_ingreso}\n"
            f"📅 Salida (Check-Out): {reserva.fecha_salida}\n"
            f"💰 Monto Total Abonado: ${reserva.total}\n\n"
            f"¡Gracias por elegirnos! Te esperamos en el hotel.\n"
        )
        
        send_mail(
            asunto,
            cuerpo_mensaje,
            'notificaciones@tu_hotel.com',
            [correo_destino],
            fail_silently=False,
        )

class ComprobanteObserver(Observer):
    def actualizar(self, reserva):
        # Vinculado a tu modelo Comprobante
        from .models import Comprobante
        Comprobante.objects.create(
            descripcion=f"Comprobante oficial para la Reserva #{reserva.id}",
            reserva=reserva
        )
        print(f"[Observer] ÉXITO: Fila de Comprobante creada en la BD.")

class PagoObserver(Observer):
    def actualizar(self, reserva):
        from .models import Pago
        # Modificamos el tipo_pago para que impacte con el nombre real
        Pago.objects.create(
            monto=reserva.total,
            reserva=reserva,
            tipo_pago="Tarjeta de Crédito / Débito" 
        )
        print(f"[Observer] ÉXITO: Registro de Pago guardado como 'Tarjeta de Crédito / Débito'.")