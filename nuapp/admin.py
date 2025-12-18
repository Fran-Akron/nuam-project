from django.contrib import admin
from .models import Persona, Colaborador, Instrumento, Calificacion

admin.site.register(Persona)
admin.site.register(Colaborador)
admin.site.register(Instrumento)
admin.site.register(Calificacion)
