from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class EspaciosPublicacionTests(TestCase):
    def test_lista_requiere_login(self):
        response = self.client.get(reverse("espacios:listar"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response.url)

    def test_autenticado_puede_ver_lista(self):
        user = User.objects.create_user("viewer", password="test-password")
        self.client.force_login(user)

        response = self.client.get(reverse("espacios:listar"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Parcela Didáctica")

    def test_ficha_y_qr_son_publicos(self):
        ficha = self.client.get(reverse("espacios:espacio_1"))
        qr = self.client.get(reverse("espacios:qr", args=["espacio_1"]))

        self.assertEqual(ficha.status_code, 200)
        self.assertEqual(qr.status_code, 200)
        self.assertEqual(qr["Content-Type"], "image/png")
        self.assertTrue(qr.content.startswith(b"\x89PNG"))

    def test_qr_desconocido_entrega_404(self):
        response = self.client.get(reverse("espacios:qr", args=["desconocido"]))
        self.assertEqual(response.status_code, 404)
