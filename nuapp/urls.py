from django.urls import path
from . import views

urlpatterns = [

    # =========================
    # HOME
    # =========================
    path("", views.home_redirect, name="home"),

    # =========================
    # AUTH
    # =========================
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("crear-cuenta/", views.crear_cuenta_view, name="crear_cuenta"),

    # =========================
    # CORE
    # =========================
    path("dashboard/", views.dashboard_view, name="dashboard"),

    # =========================
    # INSTRUMENTOS
    # =========================
    path("instrumentos/", views.instrumentos_view, name="instrumentos"),
    path("instrumentos/nuevo/", views.instrumento_form_view, name="instrumento_nuevo"),
    path(
        "instrumentos/editar/<int:instrumento_id>/",
        views.instrumento_form_view,
        name="instrumento_editar"
    ),
    path(
        "instrumentos/ver/<int:instrumento_id>/",
        views.instrumento_detalle_view,
        name="instrumento_detalle"
    ),
    path(
        "instrumentos/eliminar/<int:instrumento_id>/",
        views.instrumento_eliminar_view,
        name="instrumento_eliminar"
    ),

    # =========================
    # CALIFICACIONES
    # =========================
    path("calificaciones/", views.calificaciones_view, name="calificaciones"),
    path(
        "calificaciones/nueva/",
        views.calificacion_form_view,
        name="calificacion_nueva"
    ),
    path(
        "calificaciones/editar/<int:calificacion_id>/",
        views.calificacion_form_view,
        name="calificacion_editar"
    ),
    path(
        "calificaciones/eliminar/<int:calificacion_id>/",
        views.calificacion_eliminar_view,
        name="calificacion_eliminar"
    ),

    # =========================
    # CARGA MASIVA
    # =========================
    path("carga-masiva/", views.carga_masiva_view, name="carga_masiva"),

    # =========================
    # ADMIN
    # =========================
    path("admin/", views.admin_usuarios_view, name="admin"),
]
