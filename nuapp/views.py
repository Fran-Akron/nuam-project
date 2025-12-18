from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
import csv
from io import TextIOWrapper

from .models import Instrumento, Calificacion


# =========================================================
#   HOME / REDIRECT
# =========================================================
def home_redirect(request):
    return redirect("login")


# =========================================================
#   LOGIN / LOGOUT
# =========================================================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")

        return render(request, "nuapp/login.html", {
            "error": "Usuario o contraseña incorrectos"
        })

    return render(request, "nuapp/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# =========================================================
#   CREAR CUENTA
# =========================================================
def crear_cuenta_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if not all([username, email, password, password2]):
            return render(request, "nuapp/crear_cuenta.html", {
                "error": "Completa todos los campos."
            })

        if password != password2:
            return render(request, "nuapp/crear_cuenta.html", {
                "error": "Las contraseñas no coinciden."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "nuapp/crear_cuenta.html", {
                "error": "Usuario ya existe."
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return redirect("login")

    return render(request, "nuapp/crear_cuenta.html")


# =========================================================
#   DASHBOARD
# =========================================================
@login_required
def dashboard_view(request):
    contexto = {
        "active_page": "dashboard",
        "updated_at": timezone.localtime().strftime("%d-%m-%Y %H:%M"),
    }
    return render(request, "nuapp/dashboard.html", contexto)


# =========================================================
#   INSTRUMENTOS (LISTADO)
# =========================================================
@login_required
def instrumentos_view(request):
    instrumentos = Instrumento.objects.all().order_by("codigo")

    q = request.GET.get("q", "")
    tipo = request.GET.get("tipo", "")
    mercado = request.GET.get("mercado", "")
    estado = request.GET.get("estado", "")

    if q:
        instrumentos = instrumentos.filter(
            codigo__icontains=q
        ) | instrumentos.filter(
            nombre__icontains=q
        )

    if tipo:
        instrumentos = instrumentos.filter(tipo=tipo)

    if mercado:
        instrumentos = instrumentos.filter(mercado=mercado)

    if estado:
        instrumentos = instrumentos.filter(estado=estado)

    contexto = {
        "active_page": "instrumentos",
        "instrumentos": instrumentos,
    }

    return render(request, "nuapp/instrumentos.html", contexto)


# =========================================================
#   INSTRUMENTOS (CREAR / EDITAR)
# =========================================================
@login_required
def instrumento_form_view(request, instrumento_id=None):
    instrumento = None

    if instrumento_id:
        instrumento = get_object_or_404(Instrumento, id=instrumento_id)

    if request.method == "POST":
        data = {
            "codigo": request.POST.get("codigo"),
            "nombre": request.POST.get("nombre"),
            "tipo": request.POST.get("tipo"),
            "mercado": request.POST.get("mercado"),
            "estado": request.POST.get("estado"),
            "fecha_emision": request.POST.get("fecha_emision") or None,
            "fecha_vencimiento": request.POST.get("fecha_vencimiento") or None,
        }

        if instrumento:
            for campo, valor in data.items():
                setattr(instrumento, campo, valor)
            instrumento.save()
        else:
            Instrumento.objects.create(**data)

        return redirect("instrumentos")

    contexto = {
        "instrumento": instrumento,
        "active_page": "instrumentos",
        "tipos": Instrumento.TIPO_CHOICES,
        "mercados": Instrumento.MERCADO_CHOICES,
        "estados": Instrumento.ESTADO_CHOICES,
    }

    return render(request, "nuapp/instrumento_form.html", contexto)


# =========================================================
#   INSTRUMENTOS (VER DETALLE)
# =========================================================
@login_required
def instrumento_detalle_view(request, instrumento_id):
    instrumento = get_object_or_404(Instrumento, id=instrumento_id)

    contexto = {
        "active_page": "instrumentos",
        "instrumento": instrumento,
        "calificaciones": instrumento.calificaciones.all(),
    }

    return render(request, "nuapp/instrumento_detalle.html", contexto)


# =========================================================
#   INSTRUMENTOS (ELIMINAR)
# =========================================================
@login_required
def instrumento_eliminar_view(request, instrumento_id):
    if request.method == "POST":
        instrumento = get_object_or_404(Instrumento, id=instrumento_id)
        instrumento.delete()
    return redirect("instrumentos")


# =========================================================
#   CALIFICACIONES (LISTADO REAL)
# =========================================================
@login_required
def calificaciones_view(request):
    calificaciones = Calificacion.objects.select_related("instrumento").all()

    contexto = {
        "active_page": "calificaciones",
        "calificaciones": calificaciones,
    }

    return render(request, "nuapp/calificaciones.html", contexto)


# =========================================================
#   CARGA MASIVA CSV (BASE)
# =========================================================
@login_required
def carga_masiva_view(request):
    contexto = {
        "active_page": "carga_masiva",
    }

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        archivo = request.FILES.get("archivo")

        if not archivo or not archivo.name.endswith(".csv"):
            contexto["error"] = "Debe subir un archivo CSV válido."
            return render(request, "nuapp/carga_masiva.html", contexto)

        try:
            reader = csv.reader(TextIOWrapper(archivo, encoding="utf-8"))
            encabezados = next(reader)
            filas = list(reader)

            contexto["mensaje"] = (
                f"Archivo CSV leído correctamente. "
                f"Tipo: {tipo}. Filas: {len(filas)}"
            )

        except Exception as e:
            contexto["error"] = f"Error al procesar el archivo: {e}"

    return render(request, "nuapp/carga_masiva.html", contexto)


# =========================================================
#   ADMINISTRACIÓN DE USUARIOS
# =========================================================
@login_required
def admin_usuarios_view(request):
    usuarios = User.objects.all().order_by("username")
    contexto = {
        "active_page": "admin",
        "usuarios": usuarios,
        "total_usuarios": usuarios.count(),
        "updated_at": timezone.localtime().strftime("%d-%m-%Y %H:%M"),
    }
    return render(request, "nuapp/admin.html", contexto)
