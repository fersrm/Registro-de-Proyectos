from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from core.mixins import PermitsPositionMixin, usuario_puede_editar_proyecto

from .forms import IntegranteProyectoFormSet, ProyectoForm, RecursoProyectoFormSet
from .models import AuditoriaProyecto, Proyecto


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

            context["recurso_formset"] = RecursoProyectoFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )

        else:
            context["formset"] = IntegranteProyectoFormSet(instance=self.object)

            context["recurso_formset"] = RecursoProyectoFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.creado_por = self.request.user
        self.object.modificado_por = self.request.user
        context = self.get_context_data(form=form)
        formset = context["formset"]
        recurso_formset = context["recurso_formset"]

        integrantes_validos = formset.is_valid()
        recursos_validos = recurso_formset.is_valid()
        if not integrantes_validos or not recursos_validos:
            context["form"] = form
            context["formset"] = formset
            context["recurso_formset"] = recurso_formset
            return self.render_to_response(context)

        with transaction.atomic():
            self.object.save()
            formset.instance = self.object
            formset.save()

            recurso_formset.instance = self.object
            recurso_formset.save()

            AuditoriaProyecto.registrar(
                accion=AuditoriaProyecto.Accion.CREAR,
                proyecto=self.object,
                actor=self.request.user,
            )

        return HttpResponseRedirect(self.get_success_url())


class ProyectoUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Proyecto
    form_class = ProyectoForm
    template_name = "pages/proyectos/proyecto_form.html"
    success_url = reverse_lazy("proyectos:listar")

    def test_func(self):
        return usuario_puede_editar_proyecto(self.request.user, self.get_object())

    def handle_no_permission(self):
        raise PermissionDenied("No tienes permisos para editar este proyecto.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context["formset"] = IntegranteProyectoFormSet(
                self.request.POST, instance=self.object
            )

            context["recurso_formset"] = RecursoProyectoFormSet(
                self.request.POST, self.request.FILES, instance=self.object
            )

        else:
            context["formset"] = IntegranteProyectoFormSet(instance=self.object)

            context["recurso_formset"] = RecursoProyectoFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.modificado_por = self.request.user
        context = self.get_context_data(form=form)
        formset = context["formset"]
        recurso_formset = context["recurso_formset"]

        integrantes_validos = formset.is_valid()
        recursos_validos = recurso_formset.is_valid()
        if not integrantes_validos or not recursos_validos:
            context["form"] = form
            context["formset"] = formset
            context["recurso_formset"] = recurso_formset
            return self.render_to_response(context)

        with transaction.atomic():
            self.object.save()
            formset.instance = self.object
            formset.save()

            recurso_formset.instance = self.object
            recurso_formset.save()

            AuditoriaProyecto.registrar(
                accion=AuditoriaProyecto.Accion.MODIFICAR,
                proyecto=self.object,
                actor=self.request.user,
            )

        return HttpResponseRedirect(self.get_success_url())


class ProyectoDeleteView(PermitsPositionMixin, DeleteView):
    model = Proyecto
    success_url = reverse_lazy("proyectos:listar")

    def form_valid(self, form):
        success_url = self.get_success_url()
        with transaction.atomic():
            AuditoriaProyecto.registrar(
                accion=AuditoriaProyecto.Accion.ELIMINAR,
                proyecto=self.object,
                actor=self.request.user,
            )
            self.object.delete()
        return HttpResponseRedirect(success_url)


#### QR ######################################################
from io import BytesIO

import qrcode
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
