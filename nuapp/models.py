from django.db import models
from django.contrib.auth.models import User

# =========================
# PERSONA
# =========================
class Persona(models.Model):
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    rut_dni = models.CharField(max_length=20, unique=True)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


# =========================
# COLABORADOR
# =========================
class Colaborador(models.Model):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=50)
    nivel_acceso = models.CharField(max_length=20)
    fecha_ingreso = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.persona} - {self.cargo}"


# =========================
# INSTRUMENTO
# =========================
class Instrumento(models.Model):
    TIPO_CHOICES = [
        ("ACCION", "Acción"),
        ("BONO", "Bono"),
        ("DERIVADO", "Derivado"),
        ("OTRO", "Otro"),
    ]

    MERCADO_CHOICES = [
        ("CL", "Chile"),
        ("PE", "Perú"),
        ("CO", "Colombia"),
    ]

    ESTADO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("INACTIVO", "Inactivo"),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    mercado = models.CharField(max_length=5, choices=MERCADO_CHOICES)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="ACTIVO")

    fecha_emision = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# =========================
# CALIFICACION
# =========================
class Calificacion(models.Model):
    TIPO_CHOICES = [
        ("RIESGO", "Riesgo"),
        ("CREDITO", "Crédito"),
        ("TRIBUTARIA", "Tributaria"),
    ]

    ESTADO_CHOICES = [
        ("ACTIVA", "Activa"),
        ("INACTIVA", "Inactiva"),
    ]

    instrumento = models.ForeignKey(
        Instrumento,
        on_delete=models.CASCADE,
        related_name="calificaciones"
    )

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="ACTIVA")
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.instrumento.codigo} - {self.tipo} ({self.fecha})"
