from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# --- PARA DATOS REALES DE LAS BOLSAS ---
import yfinance as yf


def home_redirect(request):
    return redirect('login')


# =========================================================
#   FUNCIÓN AUXILIAR PARA TRAER DATOS DE YFINANCE
# =========================================================
def obtener_indice(simbolo):
    """
    Retorna el último precio de cierre del símbolo indicado.
    Si falla, retorna None.
    """
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

def obtener_fx_usd_clp():
    try:
        data = yf.Ticker("CLP=X")  # Tipo de cambio USD → CLP
        hist = data.history(period="1d")
        precio = hist["Close"].iloc[-1]
        return round(precio, 2)
    except:
        return None

# =========================================================
#   LOGIN
# =========================================================
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            # Por ahora ambos van al mismo dashboard (se puede separar luego)
            return redirect('dashboard')

        else:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })

    return render(request, 'login.html')


# =========================================================
#   CREAR CUENTA
# =========================================================
def crear_cuenta_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        pais = request.POST.get('pais')
        identificacion = request.POST.get('identificacion')

        # VALIDACIÓN CAMPOS VACÍOS
        if not all([username, email, password, password2, pais, identificacion]):
            return render(request, 'crear_cuenta.html', {
                'error': 'Por favor completa todos los campos.'
            })

        # VALIDACIÓN PASSWORDS
        if password != password2:
            return render(request, 'crear_cuenta.html', {
                'error': 'Las contraseñas no coinciden.'
            })

        # VALIDACIÓN USERNAME ÚNICO
        if User.objects.filter(username=username).exists():
            return render(request, 'crear_cuenta.html', {
                'error': 'El nombre de usuario ya está en uso.'
            })

        # VALIDACIÓN EMAIL ÚNICO
        if User.objects.filter(email=email).exists():
            return render(request, 'crear_cuenta.html', {
                'error': 'Este correo ya está registrado.'
            })

        # CREAR USUARIO
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(request, 'crear_cuenta.html')


# =========================================================
#   DASHBOARD — USA DATOS DE YFINANCE
# =========================================================
@login_required
def dashboard_view(request):
    valor_chile = obtener_indice("^IPSA")     # Bolsa Santiago
    valor_colombia = obtener_indice("EWC")    # ETF Colombia
    valor_peru = obtener_indice("EPU")        # ETF Perú
    
    usd_clp = obtener_fx_usd_clp()            # <<< NUEVO

    contexto = {
        "valor_chile": valor_chile,
        "valor_colombia": valor_colombia,
        "valor_peru": valor_peru,
        "usd_clp": usd_clp,                   # <<< NUEVO
    }

    return render(request, "dashboard.html", contexto)


# =========================================================
#   CONSULTAS Y LOGOUT
# =========================================================
@login_required
def consultas_view(request):
    return render(request, 'consultas.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# =========================================================
#   PREVIEW DE DASHBOARDS (PARA DEMO)
# =========================================================
def preview_dashboard_admin(request):
    return render(request, 'dashboard_admin.html')


def preview_dashboard_user(request):
    return render(request, 'dashboard_user.html')
