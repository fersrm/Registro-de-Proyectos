from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
from io import BytesIO
import qrcode


class EspaciosListView(LoginRequiredMixin, ListView):
    template_name = "pages/espacios/espacios_list.html"
    context_object_name = "espacios"

    def get_queryset(self):
        return [
            {
                "id": "espacio_1",
                "nombre": "Parcela Didáctica",
                "descripcion": (
                    "Espacio agrícola y tecnológico orientado a prácticas "
                    "académicas, innovación, cultivos experimentales "
                    "y sistemas de riego automatizado."
                ),
                "ubicacion": "Km 10 Camino a Pinto",
                "superficie": "5,3 hectáreas",
                "url_name": "espacios:espacio_1",
                "imagen": "img/espacios/parcela-1.webp",
            },
        ]


class Espacio1View(TemplateView):
    template_name = "pages/espacios/espacio_1.html"


def espacio_qr_view(request, espacio_id):
    rutas = {
        "espacio_1": "espacios:espacio_1",
    }

    url_name = rutas.get(espacio_id)

    if not url_name:
        return HttpResponse("Espacio no encontrado", status=404)

    url = request.build_absolute_uri(reverse(url_name))

    qr = qrcode.make(url)

    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return HttpResponse(buffer.getvalue(), content_type="image/png")
