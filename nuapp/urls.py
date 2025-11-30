from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('consultas/', views.consultas_view, name='consultas'),
    path('logout/', views.logout_view, name='logout'),
]
