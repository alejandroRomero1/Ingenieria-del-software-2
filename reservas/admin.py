from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from .models import Habitacion, Reserva, Servicio, Pago, TipoServicio

# 1. Sobrescribimos el comportamiento solo para la Habitación
@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('numero_hab', 'tipo', 'precio', 'estado')

    def changelist_view(self, request, extra_context=None):
        """
        Intercepta el clic en el botón principal 'Habitaciones'.
        Nos desvía a nuestro listado propio.
        """
        return redirect(reverse('listado_habitaciones'))
    def add_view(self, request, form_url='', extra_context=None):
        """Intercepta el botón '+ Add' y nos manda a nuestro formulario propio"""
        return redirect(reverse('registrar_habitacion'))



admin.site.register(Reserva)
admin.site.register(Servicio)
admin.site.register(Pago)
admin.site.register(TipoServicio)