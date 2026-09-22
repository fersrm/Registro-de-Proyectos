from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .adapters import NoSignupAccountAdapter
from .models import Position, Profile


class UsuarioPermisosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.restricted_position = Position.objects.create(
            user_position="Restringido",
            permission_code="RESTRICTED",
        )
        cls.admin_position = Position.objects.create(
            user_position="Administrador",
            permission_code="ADMIN",
        )
        cls.restricted = User.objects.create_user(
            "restricted",
            password="test-password",
        )
        Profile.objects.create(
            user_FK=cls.restricted,
            position_FK=cls.restricted_position,
        )
        cls.admin = User.objects.create_user("admin", password="test-password")
        Profile.objects.create(user_FK=cls.admin, position_FK=cls.admin_position)
        cls.target = User.objects.create_user("target", password="test-password")
        Profile.objects.create(
            user_FK=cls.target,
            position_FK=cls.restricted_position,
        )
        cls.no_profile = User.objects.create_user(
            "no-profile",
            password="test-password",
        )
        cls.superuser = User.objects.create_superuser(
            "root",
            "root@example.test",
            "test-password",
        )

    def test_listado_requiere_login(self):
        response = self.client.get(reverse("User"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response.url)

    def test_todo_autenticado_incluido_sin_perfil_puede_ver_listado(self):
        for user in (self.restricted, self.admin, self.no_profile, self.superuser):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                response = self.client.get(reverse("User"))
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, self.target.username)
                self.client.logout()

    def test_restricted_no_puede_desactivar_por_url_directa(self):
        self.client.force_login(self.restricted)
        response = self.client.post(reverse("UserDeactivate", args=[self.target.pk]))

        self.assertRedirects(response, reverse("Home"))
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_active)

    def test_admin_puede_desactivar(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("UserDeactivate", args=[self.target.pk]))

        self.assertRedirects(response, reverse("User"))
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_active)

    def test_controles_administrativos_reflejan_helper(self):
        self.client.force_login(self.restricted)
        restricted_response = self.client.get(reverse("User"))
        self.assertNotContains(restricted_response, "Ver usuarios inactivos")

        self.client.force_login(self.superuser)
        superuser_response = self.client.get(reverse("User"))
        self.assertContains(superuser_response, "Ver usuarios inactivos")

    def test_perfil_se_crea_si_falta(self):
        self.client.force_login(self.no_profile)
        response = self.client.get(reverse("Profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Profile.objects.filter(user_FK=self.no_profile).exists())

    def test_registro_publico_permanece_cerrado(self):
        self.assertFalse(NoSignupAccountAdapter().is_open_for_signup(None))
