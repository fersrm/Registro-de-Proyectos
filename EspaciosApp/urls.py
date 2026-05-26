from django.urls import path

from .views import (
    EspaciosListView,
    Espacio1View,
    espacio_qr_view,
)

app_name = "espacios"

urlpatterns = [
    path("", EspaciosListView.as_view(), name="listar"),
    path("espacio-1/", Espacio1View.as_view(), name="espacio_1"),
    path("<str:espacio_id>/qr/", espacio_qr_view, name="qr"),
]
