from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_redirect, name="home"),

    # AUTH
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("crear-cuenta/", views.crear_cuenta_view, name="crear_cuenta"),

    # CORE
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("instrumentos/", views.instrumentos_view, name="instrumentos"),
    path("calificaciones/", views.calificaciones_view, name="calificaciones"),
    path("carga-masiva/", views.carga_masiva_view, name="carga_masiva"),

    # ADMIN
    path("admin/", views.admin_usuarios_view, name="admin"),
]
