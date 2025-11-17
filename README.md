# NUAM - Proyecto Base (Django)

Checkpoint inicial del proyecto NUAM desarrollado en Django.  
Este documento explica cómo clonar, instalar y ejecutar el proyecto desde cero, además de detallar su estructura y resolver problemas comunes.

---

Requisitos Previos

- Python 3.10 o superior  
- Git instalado  
- PowerShell (Windows) o Terminal (macOS/Linux)  
- **Recomendación:** trabajar fuera de OneDrive para evitar errores (ej: `C:\Nuam` o `~/projects/nuam`)

---

1. Clonar repositorio

git clone https://github.com/Fran-Akron/nuam-project.git
cd nuam-project


2. python -m venv .venv
.venv\Scripts\Activate.ps1


3. Instalar dependencias
   pip install --upgrade pip
pip install -r requirements.txt

(Si no existe utilizar el siguiente código) 
pip install django
pip freeze > requirements.txt


4. Migraciones iniciales

   python manage.py migrate


5. Ejecutar servidor de desarrollo

   python manage.py runserver


Estructura del proyecto

nuam-project/
│  manage.py
│  requirements.txt
│  .gitignore
│
├── nuam_project/         # Configuración global (settings, urls, wsgi)
│
├── nuapp/                # App principal
│   ├── views.py
│   ├── urls.py
│   └── models.py
│
└── templates/            # Archivos HTML
    └── index.html


Resumiendo....

Clonar el repo

Crear y activar .venv

Instalar dependencias

Ejecutar migraciones

Correr el servidor

Crear ramas feature/* y enviar Pull Requests

