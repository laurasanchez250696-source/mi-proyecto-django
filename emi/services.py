from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from .models import Libro, Socio, Reserva


class BibliotecaService:

    @staticmethod
    def registrar_libro(isbn, titulo, autor, anio_publicacion, cantidad_total):
        if Libro.objects.filter(isbn=isbn).exists():
            raise ValidationError(f"Ya existe un libro registrado con el ISBN {isbn}.")
        if cantidad_total <= 0:
            raise ValidationError("La cantidad total de ejemplares debe ser mayor a 0.")

        libro = Libro(
            isbn=isbn,
            titulo=titulo,
            autor=autor,
            anio_publicacion=anio_publicacion,
            cantidad_total=cantidad_total,
            cantidad_disponible=cantidad_total
        )
        libro.full_clean()
        libro.save()
        return libro

    @staticmethod
    def registrar_socio(numero_socio, nombre, apellido, dni, email, activo=True):
        if Socio.objects.filter(numero_socio=numero_socio).exists():
            raise ValidationError(f"Ya existe un socio con el número {numero_socio}.")
        if Socio.objects.filter(dni=dni).exists():
            raise ValidationError(f"Ya existe un socio registrado con el DNI {dni}.")

        socio = Socio(
            numero_socio=numero_socio,
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            email=email,
            activo=activo
        )
        socio.full_clean()
        socio.save()
        return socio

    @staticmethod
    def listar_libros():
        return Libro.objects.all()

    @staticmethod
    def buscar_libros(criterio):
        return Libro.objects.filter(
            Q(isbn__iexact=criterio) |
            Q(titulo__icontains=criterio) |
            Q(autor__icontains=criterio)
        )

    @staticmethod
    def listar_socios():
        return Socio.objects.all()

    @staticmethod
    def realizar_reserva(numero_socio, isbn):
        try:
            socio = Socio.objects.get(numero_socio=numero_socio)
        except Socio.DoesNotExist:
            raise ValidationError(f"No existe ningún socio con el número {numero_socio}.")

        try:
            libro = Libro.objects.get(isbn=isbn)
        except Libro.DoesNotExist:
            raise ValidationError(f"No existe ningún libro con el ISBN {isbn}.")

        if not socio.puede_reservar():
            raise ValidationError("El socio se encuentra inactivo y no puede realizar reservas.")

        if not libro.esta_disponible():
            raise ValidationError("No hay ejemplares disponibles para este libro.")

        reserva_activa = Reserva.objects.filter(
            socio=socio,
            libro=libro,
            estado__in=[Reserva.PENDIENTE, Reserva.RETIRADA]
        ).exists()

        if reserva_activa:
            raise ValidationError("El socio ya tiene una reserva activa (pendiente o retirada) de este libro.")

        with transaction.atomic():
            libro.reservar_ejemplar()
            reserva = Reserva.objects.create(socio=socio, libro=libro)

        return reserva

    @staticmethod
    def cancelar_reserva(reserva_id):
        try:
            reserva = Reserva.objects.get(id=reserva_id)
        except Reserva.DoesNotExist:
            raise ValidationError(f"No existe ninguna reserva con ID {reserva_id}.")
        reserva.cancelar()
        return reserva

    @staticmethod
    def retirar_libro(reserva_id):
        try:
            reserva = Reserva.objects.get(id=reserva_id)
        except Reserva.DoesNotExist:
            raise ValidationError(f"No existe ninguna reserva con ID {reserva_id}.")
        reserva.retirar()
        return reserva

    @staticmethod
    def devolver_libro(reserva_id):
        try:
            reserva = Reserva.objects.get(id=reserva_id)
        except Reserva.DoesNotExist:
            raise ValidationError(f"No existe ninguna reserva con ID {reserva_id}.")
        reserva.finalizar()
        return reserva

    @staticmethod
    def listar_reservas_socio(numero_socio):
        try:
            socio = Socio.objects.get(numero_socio=numero_socio)
        except Socio.DoesNotExist:
            raise ValidationError(f"No existe ningún socio con el número {numero_socio}.")
        return Reserva.objects.filter(socio=socio).order_by('-fecha_reserva')

    @staticmethod
    def listar_todas_reservas():
        return Reserva.objects.all().order_by('-fecha_reserva')

    # --- Consultas ORM adicionales solicitadas en el punto 5 ---
    @staticmethod
    def libros_disponibles():
        return Libro.objects.filter(cantidad_disponible__gt=0)

    @staticmethod
    def libros_agotados():
        return Libro.objects.filter(cantidad_disponible=0)

    @staticmethod
    def reservas_pendientes():
        return Reserva.objects.filter(estado=Reserva.PENDIENTE)

    @staticmethod
    def reservas_por_libro(isbn):
        return Reserva.objects.filter(libro__isbn=isbn)

    @staticmethod
    def socios_activos():
        return Socio.objects.filter(activo=True)