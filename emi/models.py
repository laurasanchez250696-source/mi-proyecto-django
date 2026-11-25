from django.db import models
from django.core.exceptions import ValidationError


class Libro(models.Model):
    isbn = models.CharField(max_length=13, unique=True)
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    anio_publicacion = models.PositiveIntegerField()
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disponible = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"[{self.isbn}] {self.titulo} - {self.autor} (Disp: {self.cantidad_disponible}/{self.cantidad_total})"

    def esta_disponible(self):
        return self.cantidad_disponible > 0

    def reservar_ejemplar(self):
        if not self.esta_disponible():
            raise ValidationError("No hay ejemplares disponibles para este libro.")
        self.cantidad_disponible -= 1
        self.save()

    def liberar_ejemplar(self):
        if self.cantidad_disponible >= self.cantidad_total:
            raise ValidationError("La cantidad disponible no puede superar la cantidad total.")
        self.cantidad_disponible += 1
        self.save()

    def clean(self):
        if self.cantidad_disponible > self.cantidad_total:
            raise ValidationError({"cantidad_disponible": "No puede ser mayor que la cantidad total."})


class Socio(models.Model):
    numero_socio = models.PositiveIntegerField(unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=15, unique=True)
    email = models.EmailField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"Socio #{self.numero_socio} - {self.nombre} {self.apellido} (DNI: {self.dni}) [{estado}]"

    def puede_reservar(self):
        return self.activo


class Reserva(models.Model):
    PENDIENTE = "PENDIENTE"
    RETIRADA = "RETIRADA"
    CANCELADA = "CANCELADA"
    FINALIZADA = "FINALIZADA"

    ESTADOS = [
        (PENDIENTE, "Pendiente"),
        (RETIRADA, "Retirada"),
        (CANCELADA, "Cancelada"),
        (FINALIZADA, "Finalizada"),
    ]

    socio = models.ForeignKey(Socio, on_delete=models.PROTECT)
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=PENDIENTE)

    def __str__(self):
        return f"Reserva #{self.id} | {self.libro.titulo} -> {self.socio.nombre} {self.socio.apellido} [{self.estado}]"

    def cancelar(self):
        if self.estado != self.PENDIENTE:
            raise ValidationError("Solo se pueden cancelar reservas pendientes.")
        self.libro.liberar_ejemplar()
        self.estado = self.CANCELADA
        self.save()

    def retirar(self):
        if self.estado != self.PENDIENTE:
            raise ValidationError("La reserva no se encuentra pendiente.")
        self.estado = self.RETIRADA
        self.save()

    def finalizar(self):
        if self.estado != self.RETIRADA:
            raise ValidationError("El libro no fue retirado.")
        self.libro.liberar_ejemplar()
        self.estado = self.FINALIZADA
        self.save()
