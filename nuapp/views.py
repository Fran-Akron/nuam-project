from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Colaborador   # 👈 IMPORTANTE

# Redirige a login si entran a "/"
def home_redirect(request):
    return redirect('login')


# -------------------------------
# LOGIN
# -------------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')   # nombre de la ruta
        else:
            return render(request, 'login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })

    return render(request, 'login.html')


# -------------------------------
# DASHBOARD (requiere login)
# -------------------------------
@login_required
def dashboard_view(request):
    colaborador = Colaborador.objects.get(usuario=request.user)

    return render(request, 'dashboard.html', {
        'colaborador': colaborador
    })


# -------------------------------
# CONSULTAS (requiere login)
# -------------------------------
@login_required
def consultas_view(request):
    colaborador = Colaborador.objects.get(usuario=request.user)

    return render(request, 'consultas.html', {
        'colaborador': colaborador
    })


# -------------------------------
# LOGOUT
# -------------------------------
def logout_view(request):
    logout(request)
    return redirect('login')


def registrar_view(request):
    return render(request, 'registrar.html')


def preview_dashboard_admin(request):
    return render(request, 'dashboard_admin.html')

def preview_dashboard_user(request):
    return render(request, 'dashboard_user.html')


from django.contrib.auth.models import User

def crear_cuenta_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validaciones
        if password != password2:
            return render(request, 'crear_cuenta.html', {
                'error': 'Las contraseñas no coinciden'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'crear_cuenta.html', {
                'error': 'El nombre de usuario ya está registrado'
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'crear_cuenta.html', {
                'error': 'El correo electrónico ya está registrado'
            })

        # Crear usuario normal (no admin)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.save()

        return redirect('login')

    return render(request, 'crear_cuenta.html')
