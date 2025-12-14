from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
import yfinance as yf
import json


def home_redirect(request):
    return redirect("login")


# =========================================================
#   HELPERS: yfinance robusto con fallback de tickers
# =========================================================
def _history_first_available(simbolos, period="1d"):
    """
    Intenta varios tickers y devuelve (df, simbolo_usado).
    Si ninguno funciona, devuelve (None, None).
    """
    if isinstance(simbolos, str):
        simbolos = [simbolos]

    for sym in simbolos:
        try:
            df = yf.Ticker(sym).history(period=period)
            if df is not None and not df.empty:
                return df, sym
        except:
            continue
    return None, None


def obtener_indice(simbolos):
    """
    Último cierre disponible (1d). Retorna float o None.
    """
    df, _ = _history_first_available(simbolos, period="1d")
    if df is None or df.empty:
        return None
    try:
        return round(float(df["Close"].iloc[-1]), 2)
    except:
        return None


def obtener_historico(simbolos, period="7d"):
    """
    Retorna (fechas, cierres) para Chart.js.
    """
    df, _ = _history_first_available(simbolos, period=period)
    if df is None or df.empty:
        return [], []
    try:
        fechas = df.index.strftime("%Y-%m-%d").tolist()
        cierres = df["Close"].round(2).tolist()
        return fechas, cierres
    except:
        return [], []


def obtener_variacion_diaria(simbolos):
    """
    Calcula variación % usando 2 días (ayer vs hoy).
    Retorna float o None.
    """
    df, _ = _history_first_available(simbolos, period="2d")
    if df is None or len(df) < 2:
        return None
    try:
        cierre_ayer = float(df["Close"].iloc[-2])
        cierre_hoy = float(df["Close"].iloc[-1])
        if cierre_ayer == 0:
            return None
        var = ((cierre_hoy - cierre_ayer) / cierre_ayer) * 100
        return round(var, 2)
    except:
        return None


def tendencia_desde_variacion(variacion):
    """
    up / down / flat / None
    """
    if variacion is None:
        return None
    if variacion > 0:
        return "up"
    if variacion < 0:
        return "down"
    return "flat"


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

        return render(request, "login.html", {"error": "Usuario o contraseña incorrectos"})

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

        if not all([username, email, password, password2, pais, identificacion]):
            return render(request, "crear_cuenta.html", {"error": "Por favor completa todos los campos."})

        if password != password2:
            return render(request, "crear_cuenta.html", {"error": "Las contraseñas no coinciden."})

        if User.objects.filter(username=username).exists():
            return render(request, "crear_cuenta.html", {"error": "El nombre de usuario ya está en uso."})

        if User.objects.filter(email=email).exists():
            return render(request, "crear_cuenta.html", {"error": "Este correo ya está registrado."})

        User.objects.create_user(username=username, email=email, password=password)
        return redirect("login")

    return render(request, "crear_cuenta.html")


# =========================================================
#   DASHBOARD (mini gráficos por mercado + flechas + update)
# =========================================================
@login_required
def dashboard_view(request):

    # ✅ Fallbacks: IPSA es el más “mañoso” en Yahoo
    mercados = {
        "Chile (IPSA)": ["^IPSA", "IPSA.SN", "^IPSA.SN"],
        "Colombia (EWC)": ["EWC"],
        "Perú (EPU)": ["EPU"],
        "USD/CLP": ["CLP=X"],
    }

    # Valores actuales
    valor_chile = obtener_indice(mercados["Chile (IPSA)"])
    valor_colombia = obtener_indice(mercados["Colombia (EWC)"])
    valor_peru = obtener_indice(mercados["Perú (EPU)"])
    usd_clp = obtener_indice(mercados["USD/CLP"])

    # Variación diaria (2d)
    var_chile = obtener_variacion_diaria(mercados["Chile (IPSA)"])
    var_colombia = obtener_variacion_diaria(mercados["Colombia (EWC)"])
    var_peru = obtener_variacion_diaria(mercados["Perú (EPU)"])

    # Históricos separados (7d)
    fechas_chile, hist_chile = obtener_historico(mercados["Chile (IPSA)"], "7d")
    fechas_col, hist_col = obtener_historico(mercados["Colombia (EWC)"], "7d")
    fechas_per, hist_per = obtener_historico(mercados["Perú (EPU)"], "7d")

    # “Última actualización”
    updated_at = timezone.localtime(timezone.now()).strftime("%d-%m-%Y %H:%M")

    contexto = {
        "updated_at": updated_at,

        "valor_chile": valor_chile,
        "valor_colombia": valor_colombia,
        "valor_peru": valor_peru,
        "usd_clp": usd_clp,

        "var_chile": var_chile,
        "var_colombia": var_colombia,
        "var_peru": var_peru,

        "trend_chile": tendencia_desde_variacion(var_chile),
        "trend_colombia": tendencia_desde_variacion(var_colombia),
        "trend_peru": tendencia_desde_variacion(var_peru),

        # JSON para Chart.js (mini charts)
        "fechas_chile": json.dumps(fechas_chile),
        "hist_chile": json.dumps(hist_chile),

        "fechas_col": json.dumps(fechas_col),
        "hist_col": json.dumps(hist_col),

        "fechas_per": json.dumps(fechas_per),
        "hist_per": json.dumps(hist_per),
    }

    return render(request, "dashboard.html", contexto)


# =========================================================
#   CONSULTAS CONSOLIDADAS (valores + tablas por mercado)
# =========================================================
@login_required
def consultas_view(request):
    mercados = {
        "Chile (IPSA)": ["^IPSA", "IPSA.SN", "^IPSA.SN"],
        "Colombia (EWC)": ["EWC"],
        "Perú (EPU)": ["EPU"],
    }

    resultados_actuales = []
    historico = {}

    for nombre, simbolos in mercados.items():
        precio_actual = obtener_indice(simbolos)
        resultados_actuales.append({
            "nombre": nombre,
            "precio": precio_actual
        })

        fechas, cierres = obtener_historico(simbolos, "7d")
        historico[nombre] = list(zip(fechas, cierres))

    contexto = {
        "resultados_actuales": resultados_actuales,
        "historico": historico,
        "updated_at": timezone.localtime(timezone.now()).strftime("%d-%m-%Y %H:%M"),
    }
    return render(request, "consultas.html", contexto)


# =========================================================
#   REPORTES Y ANÁLISIS (resumen simple con variación)
# =========================================================
@login_required
def reportes_view(request):
    mercados = {
        "Chile (IPSA)": ["^IPSA", "IPSA.SN", "^IPSA.SN"],
        "Colombia (EWC)": ["EWC"],
        "Perú (EPU)": ["EPU"],
    }

    resumen = []
    variaciones = []

    for nombre, simbolos in mercados.items():
        var = obtener_variacion_diaria(simbolos)
        cierre = obtener_indice(simbolos)

        if cierre is None or var is None:
            continue

        resumen.append({
            "mercado": nombre,
            "cierre": cierre,
            "variacion": var
        })
        variaciones.append({"mercado": nombre, "variacion": var})

    mayor_alza = max(variaciones, key=lambda x: x["variacion"], default=None)
    mayor_baja = min(variaciones, key=lambda x: x["variacion"], default=None)

    contexto = {
        "updated_at": timezone.localtime(timezone.now()).strftime("%d-%m-%Y %H:%M"),
        "resumen": resumen,
        "mayor_alza": mayor_alza,
        "mayor_baja": mayor_baja,
    }
    return render(request, "reportes.html", contexto)


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


from django.utils import timezone

@login_required
def admin_view(request):
    usuarios = User.objects.all().order_by("username")
    contexto = {
        "usuarios": usuarios,
        "total_usuarios": usuarios.count(),
        "updated_at": timezone.localtime().strftime("%d-%m-%Y %H:%M"),
    }
    return render(request, "admin.html", contexto)
