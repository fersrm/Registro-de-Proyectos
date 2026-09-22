from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from ProyectosApp.models import Proyecto
from UsuarioApp.models import Position, Profile

from .middleware import UpdateLastActivityMiddleware


class HomeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        position = Position.objects.create(
            user_position="Restringido",
            permission_code="RESTRICTED",
        )
        cls.user = User.objects.create_user("home-user", password="test-password")
        cls.profile = Profile.objects.create(user_FK=cls.user, position_FK=position)
        cls.leader = User.objects.create_user("leader", password="test-password")

    def test_inicio_requiere_login(self):
        response = self.client.get(reverse("Home"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response.url)

    def test_inicio_no_carga_grafico_de_ejemplo(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("Home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "grafico_home.js")
        self.assertNotContains(response, "echarts")

    def test_inicio_resume_proyectos_y_actividad(self):
        now = timezone.now()
        User.objects.filter(pk=self.user.pk).update(last_login=now)
        Profile.objects.filter(pk=self.profile.pk).update(last_activity=now)
        proyecto = Proyecto.objects.create(
            titulo="Proyecto reciente",
            fecha_inicio=timezone.localdate(),
            empresa_organizacion="Organización",
            lugar="Inacap",
            descripcion="D" * 120,
            objetivos="O" * 60,
            trl="TRL1",
            docente_lider=self.leader,
            creado_por=self.user,
            modificado_por=self.user,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("Home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["cantidad_proyectos"], 1)
        self.assertEqual(response.context["ultimo_proyecto"], proyecto)
        self.assertIn(self.user.pk, response.context["active_users"])

    def test_superusuario_sin_perfil_renderiza_inicio_y_navegacion(self):
        superuser = User.objects.create_superuser(
            "root",
            "root@example.test",
            "test-password",
        )
        self.client.force_login(superuser)

        response = self.client.get(reverse("Home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Registro")


class UpdateLastActivityMiddlewareTests(TestCase):
    def test_actualiza_como_maximo_una_vez_dentro_de_cinco_minutos(self):
        user = User.objects.create_user("activity-user", password="test-password")
        Profile.objects.create(user_FK=user)
        request = RequestFactory().get("/")
        request.user = user
        request.resolver_match = SimpleNamespace(app_name="")
        SessionMiddleware(lambda current_request: None).process_request(request)
        middleware = UpdateLastActivityMiddleware(lambda current_request: None)

        with patch.object(Profile, "update_last_activity") as update_activity:
            middleware.process_view(request, lambda current_request: None, (), {})
            middleware.process_view(request, lambda current_request: None, (), {})

        self.assertEqual(update_activity.call_count, 1)
