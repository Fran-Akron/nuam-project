from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_redirect),
    path("login/", views.login_view, name="login"),
    path("crear-cuenta/", views.crear_cuenta_view, name="crear_cuenta"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("consultas/", views.consultas_view, name="consultas"),
    path("reportes/", views.reportes_view, name="reportes"),
    path("logout/", views.logout_view, name="logout"),
    path('admin/', views.admin_view, name='admin'),

]
