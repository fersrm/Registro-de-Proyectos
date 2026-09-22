from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import OperationalError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from core.mixins import usuario_tiene_cargo

from .forms import DendrometroForm
from .models import Dendrometro, Sincronizacion
from .services import analysis, sync
from .services.thingspeak import ThingSpeakError, fetch


class ModuleAccess(LoginRequiredMixin):
    login_url = "account_login"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_active:
            return HttpResponse("Acceso denegado.", status=403)
        return super().dispatch(request, *args, **kwargs)


class ManagerAccess(ModuleAccess):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and not usuario_tiene_cargo(request.user):
            return HttpResponse(
                "Solo ADMIN o MANAGER pueden configurar los dendrómetros.", status=403
            )
        return super().dispatch(request, *args, **kwargs)


class ContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_configure"] = usuario_tiene_cargo(self.request.user)
        return context


class ListadoView(ModuleAccess, ContextMixin, ListView):
    model = Dendrometro
    template_name = "dendometro/listado.html"
    context_object_name = "sensores"


class ConfiguracionView(ManagerAccess, ContextMixin, ListView):
    model = Dendrometro
    template_name = "dendometro/configuracion.html"
    context_object_name = "sensores"


class VisualizacionView(ModuleAccess, ContextMixin, DetailView):
    model = Dendrometro
    template_name = "dendometro/visualizacion.html"
    context_object_name = "sensor"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sensores"] = Dendrometro.objects.all()
        return context


class FormMixin(ContextMixin):
    model = Dendrometro
    form_class = DendrometroForm
    template_name = "dendometro/formulario.html"
    success_url = reverse_lazy("dendometro:configuracion")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, "Configuración del dendrómetro guardada correctamente."
        )
        return response


class CrearView(ManagerAccess, FormMixin, CreateView):
    pass


class EditarView(ManagerAccess, FormMixin, UpdateView):
    pass


@method_decorator(never_cache, name="dispatch")
class DatosView(ModuleAccess, View):
    def get(self, request, pk):
        sensor = get_object_or_404(Dendrometro, pk=pk)
        try:
            selected = int(request.GET.get("sesion", ""))
        except ValueError:
            selected = None
        return JsonResponse(
            analysis.payload(sensor, selected), json_dumps_params={"allow_nan": False}
        )


class IniciarSyncView(ModuleAccess, View):
    def post(self, request, pk):
        sensor = get_object_or_404(Dendrometro, pk=pk)
        try:
            job = sync.start(sensor)
            return JsonResponse(
                sync.status(job) if job else {"estado": "completa", "progreso": 100}
            )
        except ThingSpeakError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except OperationalError:
            return JsonResponse(
                {"error": "La base está ocupada. Vuelve a intentar en unos segundos."},
                status=503,
            )


class PasoSyncView(ModuleAccess, View):
    def post(self, request, pk, job_id):
        job = get_object_or_404(Sincronizacion, pk=job_id, dendrometro_id=pk)
        try:
            job = sync.step(job)
            return JsonResponse(sync.status(job))
        except OperationalError:
            return JsonResponse(
                {
                    "error": "La base está ocupada. La carga se puede reanudar; vuelve a intentar."
                },
                status=503,
            )


class ProbarView(ManagerAccess, View):
    def post(self, request, pk):
        sensor = get_object_or_404(Dendrometro, pk=pk)
        try:
            rows, _, _ = fetch(sensor, results=10)
            return JsonResponse(
                {
                    "ok": True,
                    "message": f"Conexión correcta. {len(rows)} lecturas numéricas recientes."
                    if rows
                    else "Conexión correcta; el campo aún no tiene lecturas numéricas.",
                }
            )
        except ThingSpeakError as exc:
            return JsonResponse({"ok": False, "message": str(exc)}, status=400)


class ExportarView(ModuleAccess, View):
    def get(self, request, pk, tipo):
        if tipo not in ("crudo", "analisis"):
            return HttpResponse("Tipo de exportación inválido.", status=400)
        sensor = get_object_or_404(Dendrometro, pk=pk)
        _, annotated, proc, _, _ = analysis.load(sensor)
        frame = annotated if tipo == "crudo" else proc.reset_index()
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="dendrometro_{sensor.pk}_{tipo}.csv"'
        )
        response["Cache-Control"] = "private, no-store"
        response.write("\ufeff")
        frame.to_csv(response, index=False)
        return response
