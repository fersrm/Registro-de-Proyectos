from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.db import transaction
from .models import Proyecto
from .forms import ProyectoForm, IntegranteProyectoFormSet
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from core.mixins import PermitsPositionMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q


class ProyectoListView(LoginRequiredMixin, ListView):
    model = Proyecto
    template_name = "pages/proyectos/proyecto_list.html"
    context_object_name = "proyectos"
    ordering = ["-creado"]

    def get_queryset(self):

        queryset = Proyecto.objects.select_related(
            "docente_lider", "creado_por"
        ).order_by("-creado")

        search_query = self.request.GET.get("search")

        if search_query:
            queryset = queryset.filter(
                Q(titulo__icontains=search_query)
                | Q(empresa_organizacion__icontains=search_query)
                | Q(docente_lider__username__icontains=search_query)
                | Q(docente_lider__first_name__icontains=search_query)
                | Q(docente_lider__last_name__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["placeholder"] = "Buscar por título, empresa o docente líder"

        context["search_query"] = self.request.GET.get("search", "")

        return context


class ProyectoDetailView(DetailView):
    model = Proyecto
    template_name = "pages/proyectos/proyecto_detail.html"
    context_object_name = "proyecto"


class ProyectoCreateView(LoginRequiredMixin, CreateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = "pages/proyectos/proyecto_form.html"
    success_url = reverse_lazy("proyectos:listar")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = IntegranteProyectoFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["formset"] = IntegranteProyectoFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.creado_por = self.request.user
            self.object.modificado_por = self.request.user
            self.object.save()

            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                return self.form_invalid(form)

        return super().form_valid(form)


#### QR ######################################################
import qrcode
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def proyecto_qr_view(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)

    url = request.build_absolute_uri(f"/proyectos/{proyecto.pk}/")

    qr = qrcode.make(url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")


###############################################################


class ProyectoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = "pages/proyectos/proyecto_form.html"
    success_url = reverse_lazy("proyectos:listar")

    def test_func(self):
        proyecto = self.get_object()
        permiso = getattr(
            self.request.user.profile.position_FK, "permission_code", "RESTRICTED"
        )

        if permiso in ["ADMIN", "MANAGER"]:
            return True

        if permiso == "RESTRICTED" and proyecto.creado_por == self.request.user:
            return True

        return False

    def handle_no_permission(self):
        raise PermissionDenied("No tienes permisos para editar este proyecto.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = IntegranteProyectoFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["formset"] = IntegranteProyectoFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["formset"]

        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.modificado_por = self.request.user
            self.object.save()

            if formset.is_valid():
                formset.instance = self.object
                formset.save()
            else:
                return self.form_invalid(form)

        return super().form_valid(form)


class ProyectoDeleteView(LoginRequiredMixin, PermitsPositionMixin, DeleteView):
    model = Proyecto
    success_url = reverse_lazy("proyectos:listar")
