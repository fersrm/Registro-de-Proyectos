from django.urls import path

from . import views

app_name = "dendometro"
urlpatterns = [
    path("", views.ListadoView.as_view(), name="listado"),
    path("configuracion/", views.ConfiguracionView.as_view(), name="configuracion"),
    path("nuevo/", views.CrearView.as_view(), name="crear"),
    path("<int:pk>/", views.VisualizacionView.as_view(), name="visualizacion"),
    path("<int:pk>/editar/", views.EditarView.as_view(), name="editar"),
    path("<int:pk>/datos/", views.DatosView.as_view(), name="datos"),
    path("<int:pk>/sincronizar/", views.IniciarSyncView.as_view(), name="sincronizar"),
    path(
        "<int:pk>/sincronizar/<uuid:job_id>/", views.PasoSyncView.as_view(), name="paso"
    ),
    path("<int:pk>/probar/", views.ProbarView.as_view(), name="probar"),
    path(
        "<int:pk>/exportar/<str:tipo>/", views.ExportarView.as_view(), name="exportar"
    ),
]
