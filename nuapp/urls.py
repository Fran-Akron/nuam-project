from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('consultas/', views.consultas_view, name='consultas'),
    path('logout/', views.logout_view, name='logout'),

    # 👉 Rutas temporales para ver los nuevos templates
    path('preview/admin/', views.preview_dashboard_admin),
    path('preview/user/', views.preview_dashboard_user),
    path('crear-cuenta/', views.crear_cuenta_view, name='crear_cuenta'),
    path('reportes/', views.reportes_view, name='reportes'),
    
    
    
]
