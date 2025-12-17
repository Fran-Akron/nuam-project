from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
import csv
from io import TextIOWrapper

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
#   INSTRUMENTOS
# =========================================================
@login_required
def instrumentos_view(request):
    contexto = {
        "active_page": "instrumentos",
    }
    return render(request, "nuapp/instrumentos.html", contexto)


# =========================================================
#   CALIFICACIONES
# =========================================================
@login_required
def calificaciones_view(request):
    contexto = {
        "active_page": "calificaciones",
    }
    return render(request, "nuapp/calificaciones.html", contexto)


# =========================================================
#   CARGA MASIVA CSV
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
                f"Archivo CSV procesado correctamente. "
                f"Tipo: {tipo}. Registros leídos: {len(filas)}"
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
