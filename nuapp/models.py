from django.db import models
from django.contrib.auth.models import User

# PERSONA
class Persona(models.Model):
    id_persona = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=50)
    rut_dni = models.CharField(max_length=20)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

# COLABORADOR
class Colaborador(models.Model):
    id_colaborador = models.AutoField(primary_key=True)
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=50)
    fecha_ingreso = models.DateField(auto_now_add=True)
    nivel_acceso = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.persona.nombre} {self.persona.apellido} - {self.cargo}"
