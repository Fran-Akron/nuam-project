from django.db.models import Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Instrumento, Calificacion


# =========================================================
#   HOME / REDIRECT
# =========================================================
def home_redirect(request):
    return redirect("login")


# =========================================================
#   LOGIN / LOGOUT
# =========================================================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")

        return render(request, "nuapp/login.html", {
            "error": "Usuario o contraseña incorrectos"
        })

    return render(request, "nuapp/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# =========================================================
#   CREAR CUENTA
# =========================================================
def crear_cuenta_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if not all([username, email, password, password2]):
            return render(request, "nuapp/crear_cuenta.html", {
                "error": "Completa todos los campos."
            })

        if password != password2:
            return render(request, "nuapp/crear_cuenta.html", {
                "error": "Las contraseñas no coinciden."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "nuapp/crear_cuenta.html", {
                "error": "Usuario ya existe."
            })

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return redirect("login")

    return render(request, "nuapp/crear_cuenta.html")


# =========================================================
#   DASHBOARD
# =========================================================

# =========================================================
#   DASHBOARD
# =========================================================
@login_required
def dashboard_view(request):
    # Instrumentos por mercado
    inst_chile = Instrumento.objects.filter(mercado="CL").count()
    inst_peru = Instrumento.objects.filter(mercado="PE").count()
    inst_colombia = Instrumento.objects.filter(mercado="CO").count()

    # Calificaciones por mercado (vía instrumento)
    cal_chile = Calificacion.objects.filter(instrumento__mercado="CL").count()
    cal_peru = Calificacion.objects.filter(instrumento__mercado="PE").count()
    cal_colombia = Calificacion.objects.filter(instrumento__mercado="CO").count()

    contexto = {
        "active_page": "dashboard",
        "updated_at": timezone.localtime().strftime("%d-%m-%Y %H:%M"),

        # Instrumentos
        "inst_chile": inst_chile,
        "inst_peru": inst_peru,
        "inst_colombia": inst_colombia,

        # Calificaciones
        "cal_chile": cal_chile,
        "cal_peru": cal_peru,
        "cal_colombia": cal_colombia,
    }

    return render(request, "nuapp/dashboard.html", contexto)





# =========================================================
#   INSTRUMENTOS (LISTADO)
# =========================================================
@login_required
def instrumentos_view(request):
    instrumentos = Instrumento.objects.all().order_by("codigo")

    q = request.GET.get("q", "")
    tipo = request.GET.get("tipo", "")
    mercado = request.GET.get("mercado", "")
    estado = request.GET.get("estado", "")

    if q:
        instrumentos = instrumentos.filter(
            codigo__icontains=q
        ) | instrumentos.filter(
            nombre__icontains=q
        )

    if tipo:
        instrumentos = instrumentos.filter(tipo=tipo)

    if mercado:
        instrumentos = instrumentos.filter(mercado=mercado)

    if estado:
        instrumentos = instrumentos.filter(estado=estado)

    contexto = {
        "active_page": "instrumentos",
        "instrumentos": instrumentos,
    }
    return render(request, "nuapp/instrumentos.html", contexto)


# =========================================================
#   INSTRUMENTOS (CREAR / EDITAR)
# =========================================================
@login_required
def instrumento_form_view(request, instrumento_id=None):
    instrumento = None

    if instrumento_id:
        instrumento = get_object_or_404(Instrumento, id=instrumento_id)

    if request.method == "POST":
        data = {
            "codigo": request.POST.get("codigo"),
            "nombre": request.POST.get("nombre"),
            "tipo": request.POST.get("tipo"),
            "mercado": request.POST.get("mercado"),
            "estado": request.POST.get("estado"),
            "fecha_emision": request.POST.get("fecha_emision") or None,
            "fecha_vencimiento": request.POST.get("fecha_vencimiento") or None,
        }

        if instrumento:
            for campo, valor in data.items():
                setattr(instrumento, campo, valor)
            instrumento.save()
        else:
            Instrumento.objects.create(**data)

        return redirect("instrumentos")

    contexto = {
        "instrumento": instrumento,
        "active_page": "instrumentos",
        "tipos": Instrumento.TIPO_CHOICES,
        "mercados": Instrumento.MERCADO_CHOICES,
        "estados": Instrumento.ESTADO_CHOICES,
    }
    return render(request, "nuapp/instrumento_form.html", contexto)


# =========================================================
#   INSTRUMENTOS (VER DETALLE)
# =========================================================
@login_required
def instrumento_detalle_view(request, instrumento_id):
    instrumento = get_object_or_404(Instrumento, id=instrumento_id)

    contexto = {
        "active_page": "instrumentos",
        "instrumento": instrumento,
        "calificaciones": instrumento.calificaciones.all(),
    }
    return render(request, "nuapp/instrumento_detalle.html", contexto)


# =========================================================
#   INSTRUMENTOS (ELIMINAR)
# =========================================================
@login_required
def instrumento_eliminar_view(request, instrumento_id):
    if request.method == "POST":
        instrumento = get_object_or_404(Instrumento, id=instrumento_id)
        instrumento.delete()
    return redirect("instrumentos")


# =========================================================
#   CALIFICACIONES (LISTADO + FILTROS)
# =========================================================
@login_required
def calificaciones_view(request):
    calificaciones = (
        Calificacion.objects
        .select_related("instrumento")
        .order_by("-fecha")
    )

    codigo = request.GET.get("codigo", "")
    tipo = request.GET.get("tipo", "")
    estado = request.GET.get("estado", "")
    fecha_desde = request.GET.get("fecha_desde", "")
    fecha_hasta = request.GET.get("fecha_hasta", "")

    # Código de calificación (CAL-12 o 12)
    if codigo:
        codigo = codigo.replace("CAL-", "")
        if codigo.isdigit():
            calificaciones = calificaciones.filter(id=codigo)

    if tipo:
        calificaciones = calificaciones.filter(tipo=tipo)

    if estado:
        calificaciones = calificaciones.filter(estado=estado)

    if fecha_desde:
        calificaciones = calificaciones.filter(fecha__gte=fecha_desde)

    if fecha_hasta:
        calificaciones = calificaciones.filter(fecha__lte=fecha_hasta)

    contexto = {
        "active_page": "calificaciones",
        "calificaciones": calificaciones,
        "tipos": Calificacion.TIPO_CHOICES,
        "estados": Calificacion.ESTADO_CHOICES,
    }
    return render(request, "nuapp/calificaciones.html", contexto)


# =========================================================
#   CALIFICACIONES (CREAR / EDITAR)
# =========================================================
@login_required
def calificacion_form_view(request, calificacion_id=None):
    calificacion = None
    instrumentos = Instrumento.objects.all().order_by("codigo")

    if calificacion_id:
        calificacion = get_object_or_404(Calificacion, id=calificacion_id)

    if request.method == "POST":
        instrumento_id = request.POST.get("instrumento")
        tipo = request.POST.get("tipo")
        estado = request.POST.get("estado")
        fecha = request.POST.get("fecha")
        monto = request.POST.get("monto") or None

        instrumento = get_object_or_404(Instrumento, id=instrumento_id)

        if calificacion:
            calificacion.instrumento = instrumento
            calificacion.tipo = tipo
            calificacion.estado = estado
            calificacion.fecha = fecha
            calificacion.monto = monto
            calificacion.save()
        else:
            Calificacion.objects.create(
                instrumento=instrumento,
                tipo=tipo,
                estado=estado,
                fecha=fecha,
                monto=monto
            )

        return redirect("calificaciones")

    contexto = {
        "active_page": "calificaciones",
        "calificacion": calificacion,
        "instrumentos": instrumentos,
        "tipos": Calificacion.TIPO_CHOICES,
        "estados": Calificacion.ESTADO_CHOICES,
    }
    return render(request, "nuapp/calificacion_form.html", contexto)


# =========================================================
#   CALIFICACIONES (ELIMINAR)
# =========================================================
@login_required
def calificacion_eliminar_view(request, calificacion_id):
    calificacion = get_object_or_404(Calificacion, id=calificacion_id)

    if request.method == "POST":
        calificacion.delete()

    return redirect("calificaciones")


# =========================================================
#   CARGA MASIVA (ESTABLE - NO TOCAR)
# =========================================================
import io
import csv
from django.db import transaction
from django.utils.dateparse import parse_date

@login_required
def carga_masiva_view(request):
    contexto = {"active_page": "carga_masiva"}

    if request.method == "POST":
        tipo = request.POST.get("tipo")
        archivo = request.FILES.get("archivo")
        mercado = request.POST.get("mercado")

        if not archivo:
            contexto["error"] = "Debes seleccionar un archivo CSV."
            return render(request, "nuapp/carga_masiva.html", contexto)

        if tipo == "INSTRUMENTOS":
            if not mercado:
                contexto["error"] = "Selecciona un mercado para cargar instrumentos."
                return render(request, "nuapp/carga_masiva.html", contexto)

            ok, msg = cargar_instrumentos_csv(archivo, mercado)
        elif tipo == "CALIFICACIONES":
            ok, msg = cargar_calificaciones_csv(archivo)
        else:
            contexto["error"] = "Tipo de carga no reconocido."
            return render(request, "nuapp/carga_masiva.html", contexto)

        if ok:
            contexto["mensaje"] = msg
        else:
            contexto["error"] = msg

    return render(request, "nuapp/carga_masiva.html", contexto)


def _abrir_csv(file_obj):
    try:
        return io.TextIOWrapper(file_obj, encoding="utf-8-sig"), "utf-8-sig"
    except UnicodeDecodeError:
        file_obj.seek(0)
        return io.TextIOWrapper(file_obj, encoding="latin-1"), "latin-1"


def cargar_instrumentos_csv(archivo, mercado):
    encabezados = ["codigo", "nombre", "tipo", "estado", "fecha_emision", "fecha_vencimiento"]
    wrapper, _ = _abrir_csv(archivo)
    reader = csv.DictReader(wrapper, delimiter=",")

    if reader.fieldnames != encabezados:
        return False, "Encabezados inválidos para instrumentos."

    creados = 0
    with transaction.atomic():
        for row in reader:
            codigo = (row["codigo"] or "").strip()
            if not codigo:
                continue

            Instrumento.objects.update_or_create(
                codigo=codigo,
                defaults={
                    "nombre": (row["nombre"] or "").strip(),
                    "tipo": (row["tipo"] or "").strip(),
                    "estado": (row["estado"] or "").strip(),
                    "mercado": mercado,
                    "fecha_emision": parse_date(row["fecha_emision"] or None),
                    "fecha_vencimiento": parse_date(row["fecha_vencimiento"] or None),
                },
            )
            creados += 1

    return True, f"Instrumentos procesados correctamente: {creados}"


def cargar_calificaciones_csv(archivo):
    encabezados = ["codigo_instrumento", "tipo", "estado", "fecha", "monto"]
    wrapper, _ = _abrir_csv(archivo)
    reader = csv.DictReader(wrapper, delimiter=",")

    if reader.fieldnames != encabezados:
        return False, "Encabezados inválidos para calificaciones."

    creadas = 0
    with transaction.atomic():
        for row in reader:
            codigo_instr = (row["codigo_instrumento"] or "").strip()
            if not codigo_instr:
                continue

            instrumento = Instrumento.objects.get(codigo=codigo_instr)

            Calificacion.objects.create(
                instrumento=instrumento,
                tipo=(row["tipo"] or "").strip(),
                estado=(row["estado"] or "").strip(),
                fecha=parse_date(row["fecha"] or None),
                monto=row["monto"] or None,
            )
            creadas += 1

    return True, f"Calificaciones procesadas correctamente: {creadas}"


# =========================================================
#   ADMINISTRACIÓN DE USUARIOS
# =========================================================
@login_required
def admin_usuarios_view(request):
    usuarios = User.objects.all().order_by("username")
    contexto = {
        "active_page": "admin",
        "usuarios": usuarios,
        "total_usuarios": usuarios.count(),
        "updated_at": timezone.localtime().strftime("%d-%m-%Y %H:%M"),
    }
    return render(request, "nuapp/admin.html", contexto)


# =========================================================
#   REPORTES (INSTRUMENTOS / CALIFICACIONES / POR PAÍS)
# =========================================================
@login_required
def reportes_view(request):
    # -------------------------
    # Totales generales
    # -------------------------
    total_instrumentos = Instrumento.objects.count()
    total_calificaciones = Calificacion.objects.count()

    # -------------------------
    # Reporte Instrumentos
    # -------------------------
    instrumentos_por_tipo = (
        Instrumento.objects
        .values("tipo")
        .annotate(total=Count("id"))
        .order_by("tipo")
    )

    instrumentos_por_estado = (
        Instrumento.objects
        .values("estado")
        .annotate(total=Count("id"))
        .order_by("estado")
    )

    instrumentos_por_mercado = (
        Instrumento.objects
        .values("mercado")
        .annotate(total=Count("id"))
        .order_by("mercado")
    )

    # -------------------------
    # Reporte Calificaciones
    # -------------------------
    calificaciones_por_tipo = (
        Calificacion.objects
        .values("tipo")
        .annotate(total=Count("id"))
        .order_by("tipo")
    )

    calificaciones_por_estado = (
        Calificacion.objects
        .values("estado")
        .annotate(total=Count("id"))
        .order_by("estado")
    )

    monto_total_calificaciones = (
        Calificacion.objects.aggregate(total=Sum("monto"))["total"] or 0
    )

    # -------------------------
    # Reporte por País (Mercado)
    # Instrumentos por mercado + Calificaciones activas por mercado
    # + Suma montos por mercado (solo activas)
    # -------------------------
    # Base instrumentos por mercado
    base = (
        Instrumento.objects
        .values("mercado")
        .annotate(
            instrumentos=Count("id"),
            calificaciones_activas=Count(
                "calificaciones",
                filter=Calificacion.objects.filter(estado="ACTIVA").query.where
            )
        )
    )

    # ⚠️ El filtro anterior con .query.where puede variar según versión.
    # Para hacerlo 100% compatible, lo reemplazaremos en el Paso 2 si da problemas.
    # Por ahora, dejamos el reporte por mercado simple y estable:

    paises = []
    for codigo, nombre in Instrumento.MERCADO_CHOICES:
        instrumentos_qs = Instrumento.objects.filter(mercado=codigo)
        calif_activas_qs = Calificacion.objects.filter(instrumento__mercado=codigo, estado="ACTIVA")

        paises.append({
            "mercado": codigo,
            "mercado_label": nombre,
            "instrumentos": instrumentos_qs.count(),
            "calificaciones_activas": calif_activas_qs.count(),
            "monto_activo": calif_activas_qs.aggregate(total=Sum("monto"))["total"] or 0,
        })

    contexto = {
        "active_page": "reportes",

        "total_instrumentos": total_instrumentos,
        "total_calificaciones": total_calificaciones,

        "instrumentos_por_tipo": instrumentos_por_tipo,
        "instrumentos_por_estado": instrumentos_por_estado,
        "instrumentos_por_mercado": instrumentos_por_mercado,

        "calificaciones_por_tipo": calificaciones_por_tipo,
        "calificaciones_por_estado": calificaciones_por_estado,
        "monto_total_calificaciones": monto_total_calificaciones,

        "paises": paises,
    }
    return render(request, "nuapp/reportes.html", contexto)


# =========================================================
#   EXPORTAR CSV - INSTRUMENTOS
# =========================================================
import csv
from django.http import HttpResponse

@login_required
def exportar_instrumentos_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="instrumentos.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Codigo", "Nombre", "Tipo", "Mercado",
        "Estado", "Fecha Emision", "Fecha Vencimiento"
    ])

    instrumentos = Instrumento.objects.all().order_by("codigo")

    for i in instrumentos:
        writer.writerow([
            i.codigo,
            i.nombre,
            i.get_tipo_display(),
            i.get_mercado_display(),
            i.get_estado_display(),
            i.fecha_emision or "",
            i.fecha_vencimiento or "",
        ])

    return response


# =========================================================
#   EXPORTAR CSV - CALIFICACIONES
# =========================================================
@login_required
def exportar_calificaciones_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="calificaciones.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Codigo Calificacion", "Codigo Instrumento",
        "Tipo", "Estado", "Fecha", "Monto"
    ])

    calificaciones = (
        Calificacion.objects
        .select_related("instrumento")
        .order_by("-fecha")
    )

    for c in calificaciones:
        writer.writerow([
            f"CAL-{c.id}",
            c.instrumento.codigo,
            c.get_tipo_display(),
            c.get_estado_display(),
            c.fecha,
            c.monto or "",
        ])

    return response


# =========================================================
#   EXPORTACIÓN CSV
# =========================================================
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def exportar_instrumentos_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="instrumentos.csv"'

    writer = csv.writer(response)
    writer.writerow([
        "Código",
        "Nombre",
        "Tipo",
        "Mercado",
        "Estado",
        "Fecha Emisión",
        "Fecha Vencimiento",
    ])

    instrumentos = Instrumento.objects.all().order_by("codigo")

    for i in instrumentos:
        writer.writerow([
            i.codigo,
            i.nombre,
            i.get_tipo_display(),
            i.get_mercado_display(),
            i.estado,
            i.fecha_emision or "",
            i.fecha_vencimiento or "",
        ])

    return response
