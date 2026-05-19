from django.urls import path
from .views import (
    ProyectoListView,
    ProyectoCreateView,
    ProyectoDetailView,
    ProyectoUpdateView,
    ProyectoDeleteView,
    proyecto_qr_view,
)

app_name = "proyectos"

urlpatterns = [
    path("", ProyectoListView.as_view(), name="listar"),
    path("crear/", ProyectoCreateView.as_view(), name="crear"),
    path("<int:pk>/", ProyectoDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", ProyectoUpdateView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", ProyectoDeleteView.as_view(), name="eliminar"),
    path("<int:pk>/qr/", proyecto_qr_view, name="qr"),
]
