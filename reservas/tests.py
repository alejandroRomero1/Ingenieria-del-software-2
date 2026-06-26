from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Habitacion, Reserva, Pago, Comprobante
from .repositories import ReservaRepository
from datetime import date

class ReservaOperacionCriticaTestCase(TestCase):

    def setUp(self):
        """Configuración inicial para cada escenario de prueba"""
        self.usuario = User.objects.create_user(username='cliente_test', password='password123')
        
        self.habitacion = Habitacion.objects.create(
            numero_hab=101,
            tipo="Standard",
            capacidad=2,
            precio=100.00,
            estado="Disponible",
            descripcion="Habitación de prueba estándar"
        )

    # =====================================================================
    # 1. TESTS DEL CLIENTE (RESERVA Y CONSULTAS)
    # =====================================================================

    def test_contrato_confirmar_reserva_curso_normal(self):
        """
        [Mapea Paso 7.1] TEST CURSO NORMAL: Verifica que al confirmar la reserva
        se persista y se ejecuten todos los observadores automáticamente.
        """
        reserva = Reserva(
            fecha_ingreso=date(2026, 7, 1),
            fecha_salida=date(2026, 7, 5),
            total=400.00,
            usuario=self.usuario,
            habitacion=self.habitacion
        )

        # Ejecutamos la operación crítica
        reserva.confirmar_reserva()

        # Verificaciones de Postcondición (Observer)
        self.assertIsNotNone(reserva.id)
        self.habitacion.refresh_from_db()
        self.assertEqual(self.habitacion.estado, "Ocupada")
        self.assertTrue(Pago.objects.filter(reserva=reserva).exists())
        self.assertTrue(Comprobante.objects.filter(reserva=reserva).exists())

    def test_buscar_habitaciones_no_disponibles_curso_alternativo(self):
        """
        [Mapea Paso 2.1.1] TEST CURSO ALTERNATIVO: Si la habitación ya está reservada 
        en esas fechas, la búsqueda debe devolver una lista vacía.
        """
        Reserva.objects.create(
            fecha_ingreso=date(2026, 7, 1),
            fecha_salida=date(2026, 7, 7),
            total=600.00,
            usuario=self.usuario,
            habitacion=self.habitacion
        )

        habitaciones_libres = ReservaRepository.buscar_habitaciones_disponibles(
            date(2026, 7, 2), 
            date(2026, 7, 5)
        )

        self.assertNotIn(self.habitacion, habitaciones_libres, "Error: Se listó una habitación que ya estaba ocupada.")

    def test_calcular_total_reserva_regla_de_negocio(self):
        """
        TEST REGLA DE NEGOCIO: Verifica que la regla de negocio del repositorio
        asigne al menos 1 día de estadía si el ingreso y egreso ocurren el mismo día.
        """
        total_calculado = ReservaRepository.calcular_total_reserva(
            "2026-07-10", 
            "2026-07-10", 
            self.habitacion.precio
        )
        self.assertEqual(total_calculado, 100.00)

    def test_cliente_no_logueado_redirige_a_login_curso_alternativo(self):
        """
        [Mapea Paso 3.1.1] TEST CURSO ALTERNATIVO: Si un usuario anónimo intenta 
        acceder a la pantalla de confirmación, el sistema DEBE rechazarlo y redirigirlo.
        """
        url = reverse('confirmar_reserva', args=[self.habitacion.id])
        respuesta = self.client.get(f"{url}?inicio=2026-07-01&fin=2026-07-05")

        self.assertEqual(respuesta.status_code, 302, "Error: El sistema permitió el acceso a un cliente no logueado.")

    # =====================================================================
    # 2. TESTS DEL ADMINISTRADOR (CONTRATOS DE HABITACIÓN)
    # =====================================================================

    def test_contrato_crear_nueva_habitacion_exitoso(self):
        """
        [Mapea Caso de Uso: Registrar Habitación - Paso 4.1] TEST CURSO NORMAL: 
        Verifica las poscondiciones del contrato al dar de alta una habitación.
        """
        # Simulamos la acción del administrador creando la habitación 102
        nueva_hab = Habitacion.objects.create(
            numero_hab=102,
            tipo="Suite",
            capacidad=3,
            precio=180.00,
            estado="Disponible",
            descripcion="Suite presidencial de prueba"
        )

        # Verificaciones de Postcondición según tu contrato
        self.assertIsNotNone(nueva_hab.id)
        self.assertEqual(nueva_hab.numero_hab, 102)
        self.assertEqual(nueva_hab.estado, "Disponible") # Estado inicial requerido

    def test_contrato_crear_habitacion_duplicada_excepcion(self):
        """
        [Mapea Caso de Uso: Registrar Habitación - Paso 4.1.1] TEST CURSO ALTERNATIVO:
        Verifica la excepción del contrato si se intenta duplicar el número de habitación.
        """
        # Intentamos crear una habitación con el número 101 (que ya creamos en el setUp)
        # Django maneja esto con un IntegrityError si 'numero_hab' es un campo Unique en tu modelo
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            Habitacion.objects.create(
                numero_hab=101,  # ¡DUPLICADO!
                tipo="Matrimonial",
                capacidad=2,
                precio=120.00,
                estado="Disponible",
                descripcion="Intento de duplicado"
            )

    def test_contrato_actualizar_datos_habitacion_exitoso(self):
        """
        [Mapea Caso de Uso: Modificar Habitación - Paso 5.1] TEST CURSO NORMAL:
        Verifica que los atributos cambien y se persistan correctamente en la BD.
        """
        # Modificamos los datos de la habitación 101 que vino del setUp
        self.habitacion.tipo = "Standard VIP"
        self.habitacion.precio = 135.00
        self.habitacion.descripcion = "Descripción modificada con aire acondicionado"
        self.habitacion.save()

        # Forzamos la lectura fresca desde la base de datos PostgreSQL
        self.habitacion.refresh_from_db()

        # Verificaciones del contrato
        self.assertEqual(self.habitacion.tipo, "Standard VIP")
        self.assertEqual(self.habitacion.precio, 135.00)
        self.assertEqual(self.habitacion.descripcion, "Descripción modificada con aire acondicionado")

    def test_contrato_actualizar_numero_duplicado_excepcion(self):
        """
        [Mapea Caso de Uso: Modificar Habitación - Paso 5.1.1] TEST CURSO ALTERNATIVO:
        Verifica la excepción si al modificar una habitación le asignamos el número de otra.
        """
        # Creamos una segunda habitación (la 102)
        Habitacion.objects.create(
            numero_hab=102,
            tipo="Suite",
            capacidad=2,
            precio=200.00,
            estado="Disponible",
            descripcion="Habitación de apoyo"
        )

        # Intentamos editar la habitación 101 para que pase a llamarse 102 (Colisión)
        from django.db import IntegrityError
        
        self.habitacion.numero_hab = 102
        
        with self.assertRaises(IntegrityError):
            self.habitacion.save()


            