from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('nuapp.urls')),   # <- esta línea conecta tu app
]
