from django.contrib import admin
from .models import Habitacion, Reserva, Servicio, Pago, TipoServicio

# Esto hará que las tablas aparezcan en el panel /admin
admin.site.register(Habitacion)
admin.site.register(Reserva)
admin.site.register(Servicio)
admin.site.register(Pago)
admin.site.register(TipoServicio)