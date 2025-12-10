from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import yfinance as yf
import json


def home_redirect(request):
    return redirect('login')


# =========================================================
#   FUNCIÓN AUXILIAR: PRECIO ACTUAL
# =========================================================
def obtener_indice(simbolo):
    try:
        data = yf.Ticker(simbolo)
        hist = data.history(period="1d")

        if hist.empty:
            print(f"⚠ No data for {simbolo}")
            return None

        precio = hist["Close"].iloc[-1]
        return round(float(precio), 2)

    except Exception as e:
        print(f"❌ Error obteniendo {simbolo}: {e}")
        return None


# =========================================================
#   FUNCIÓN AUXILIAR: HISTÓRICO 7 DÍAS
# =========================================================
def obtener_historico(simbolo):
    try:
        data = yf.Ticker(simbolo).history(period="7d")
        fechas = data.index.strftime("%Y-%m-%d").tolist()
        cierres = data["Close"].round(2).tolist()
        return fechas, cierres
    except:
        return [], []


# =========================================================
#   LOGIN
# =========================================================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "login.html", {
                "error": "Usuario o contraseña incorrectos"
            })

    return render(request, "login.html")


# =========================================================
#   CREAR CUENTA
# =========================================================
def crear_cuenta_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        pais = request.POST.get("pais")
        identificacion = request.POST.get("identificacion")

        # Validación campos
        if not all([username, email, password, password2, pais, identificacion]):
            return render(request, "crear_cuenta.html", {
                "error": "Por favor completa todos los campos."
            })

        if password != password2:
            return render(request, "crear_cuenta.html", {
                "error": "Las contraseñas no coinciden."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "crear_cuenta.html", {
                "error": "El nombre de usuario ya está en uso."
            })

        if User.objects.filter(email=email).exists():
            return render(request, "crear_cuenta.html", {
                "error": "Este correo ya está registrado."
            })

        User.objects.create_user(username=username, email=email, password=password)
        return redirect("login")

    return render(request, "crear_cuenta.html")


# =========================================================
#   DASHBOARD (DATOS REALES + GRÁFICO)
# =========================================================
@login_required
def dashboard_view(request):

    # Precios actuales
    valor_chile = obtener_indice("^IPSA")
    valor_colombia = obtener_indice("EWC")
    valor_peru = obtener_indice("EPU")
    valor_dolar = obtener_indice("CLP=X")

    # Históricos 7 días
    fechas_ipsa, hist_ipsa = obtener_historico("^IPSA")
    _, hist_ewc = obtener_historico("EWC")
    _, hist_epu = obtener_historico("EPU")

    contexto = {
        "valor_chile": valor_chile,
        "valor_colombia": valor_colombia,
        "valor_peru": valor_peru,
        "valor_dolar": valor_dolar,

        # Datos para Chart.js
        "fechas": json.dumps(fechas_ipsa),
        "hist_ipsa": json.dumps(hist_ipsa),
        "hist_ewc": json.dumps(hist_ewc),
        "hist_epu": json.dumps(hist_epu),
    }

    return render(request, "dashboard.html", contexto)


# =========================================================
#   CONSULTAS (VERSIÓN SIMPLE UNIVERSIDAD)
# =========================================================
# =========================================================
#   CONSULTAS CONSOLIDADAS — DATOS REALES
# =========================================================
@login_required
def consultas_view(request):
    # Tickers usados en NUAM
    tickers = {
        "Chile (IPSA)": "^IPSA",
        "Colombia (EWC)": "EWC",
        "Perú (EPU)": "EPU",
    }

    resultados_actuales = []
    historico = {}

    for nombre, simbolo in tickers.items():

        # --- Precio actual ---
        try:
            data = yf.Ticker(simbolo).history(period="1d")
            precio_actual = round(float(data["Close"].iloc[-1]), 2)
        except:
            precio_actual = None

        resultados_actuales.append({
            "nombre": nombre,
            "simbolo": simbolo,
            "precio": precio_actual
        })

        # --- Historial (7 días) ---
        try:
            hist = yf.Ticker(simbolo).history(period="7d")
            fechas = hist.index.strftime("%Y-%m-%d").tolist()
            cierres = hist["Close"].round(2).tolist()
            historico[nombre] = list(zip(fechas, cierres))
        except:
            historico[nombre] = []

    contexto = {
        "resultados_actuales": resultados_actuales,
        "historico": historico,
    }

    return render(request, "consultas.html", contexto)

# =========================================================
#   LOGOUT
# =========================================================
def logout_view(request):
    logout(request)
    return redirect("login")


def preview_dashboard_admin(request):
    return render(request, "dashboard_admin.html")


def preview_dashboard_user(request):
    return render(request, "dashboard_user.html")
