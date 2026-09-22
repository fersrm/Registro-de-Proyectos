from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from UsuarioApp.models import Position, Profile

from .models import (
    AuditoriaProyecto,
    IntegranteProyecto,
    Proyecto,
    RecursoProyecto,
)


class ProyectoTestBase(TestCase):
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
        cls.creator = User.objects.create_user("creator", password="test-password")
        Profile.objects.create(
            user_FK=cls.creator,
            position_FK=cls.restricted_position,
        )
        cls.admin = User.objects.create_user("admin", password="test-password")
        Profile.objects.create(user_FK=cls.admin, position_FK=cls.admin_position)
        cls.no_profile = User.objects.create_user(
            "no-profile",
            password="test-password",
        )
        cls.superuser = User.objects.create_superuser(
            "root",
            "root@example.test",
            "test-password",
        )
        cls.leader = User.objects.create_user("leader", password="test-password")

    def project_data(self, **overrides):
        data = {
            "titulo": "Proyecto de prueba",
            "fecha_inicio": timezone.localdate().isoformat(),
            "empresa_organizacion": "Organización de prueba",
            "lugar": "Inacap",
            "descripcion": "D" * 120,
            "objetivos": "O" * 60,
            "trl": "TRL1",
            "docente_lider": str(self.leader.pk),
            "integrantes-TOTAL_FORMS": "0",
            "integrantes-INITIAL_FORMS": "0",
            "integrantes-MIN_NUM_FORMS": "0",
            "integrantes-MAX_NUM_FORMS": "1000",
            "recursos-TOTAL_FORMS": "0",
            "recursos-INITIAL_FORMS": "0",
            "recursos-MIN_NUM_FORMS": "0",
            "recursos-MAX_NUM_FORMS": "1000",
        }
        data.update(overrides)
        return data

    def create_project(self, *, creator=None, title="Proyecto existente"):
        return Proyecto.objects.create(
            titulo=title,
            fecha_inicio=timezone.localdate(),
            empresa_organizacion="Organización",
            lugar="Inacap",
            descripcion="D" * 120,
            objetivos="O" * 60,
            trl="TRL1",
            docente_lider=self.leader,
            creado_por=creator or self.creator,
            modificado_por=creator or self.creator,
        )


class ProyectoAtomicidadAuditoriaTests(ProyectoTestBase):
    def test_usuario_sin_perfil_puede_crear_y_genera_auditoria(self):
        self.client.force_login(self.no_profile)
        response = self.client.post(
            reverse("proyectos:crear"),
            self.project_data(
                **{
                    "recursos-TOTAL_FORMS": "1",
                    "recursos-0-titulo": "Sitio del proyecto",
                    "recursos-0-url": "https://example.test/recurso",
                    "recursos-0-descripcion": "Referencia",
                }
            ),
        )

        self.assertEqual(response.status_code, 302)
        proyecto = Proyecto.objects.get()
        self.assertEqual(proyecto.creado_por, self.no_profile)
        evento = AuditoriaProyecto.objects.get()
        self.assertEqual(evento.accion, AuditoriaProyecto.Accion.CREAR)
        self.assertEqual(evento.actor, self.no_profile)
        self.assertEqual(evento.proyecto, proyecto)

    def test_recurso_invalido_no_persiste_proyecto_ni_auditoria(self):
        self.client.force_login(self.creator)
        response = self.client.post(
            reverse("proyectos:crear"),
            self.project_data(
                **{
                    "recursos-TOTAL_FORMS": "1",
                    "recursos-0-titulo": "Recurso sin origen",
                    "recursos-0-descripcion": "Inválido",
                }
            ),
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Debe ingresar un recurso válido")
        self.assertFalse(Proyecto.objects.exists())
        self.assertFalse(AuditoriaProyecto.objects.exists())

    def test_fallo_de_auditoria_revierte_la_creacion_completa(self):
        self.client.force_login(self.creator)

        with (
            patch.object(
                AuditoriaProyecto,
                "registrar",
                side_effect=RuntimeError("fallo simulado de auditoría"),
            ),
            self.assertRaisesMessage(RuntimeError, "fallo simulado de auditoría"),
        ):
            self.client.post(reverse("proyectos:crear"), self.project_data())

        self.assertFalse(Proyecto.objects.exists())
        self.assertFalse(AuditoriaProyecto.objects.exists())

    def test_edicion_invalida_no_cambia_principal_ni_auditoria(self):
        proyecto = self.create_project()
        self.client.force_login(self.creator)
        response = self.client.post(
            reverse("proyectos:editar", args=[proyecto.pk]),
            self.project_data(
                titulo="Título que no debe persistir",
                **{
                    "recursos-TOTAL_FORMS": "1",
                    "recursos-0-titulo": "Recurso inválido",
                },
            ),
        )

        self.assertEqual(response.status_code, 200)
        proyecto.refresh_from_db()
        self.assertEqual(proyecto.titulo, "Proyecto existente")
        self.assertFalse(AuditoriaProyecto.objects.exists())

    def test_cambio_solo_en_integrante_genera_un_evento_modificar(self):
        proyecto = self.create_project()
        integrante = IntegranteProyecto.objects.create(
            proyecto=proyecto,
            nombre="Nombre original",
            rol="estudiante",
        )
        self.client.force_login(self.creator)
        response = self.client.post(
            reverse("proyectos:editar", args=[proyecto.pk]),
            self.project_data(
                titulo=proyecto.titulo,
                **{
                    "integrantes-TOTAL_FORMS": "1",
                    "integrantes-INITIAL_FORMS": "1",
                    "integrantes-0-id": str(integrante.pk),
                    "integrantes-0-nombre": "Nombre actualizado",
                    "integrantes-0-rol": "estudiante",
                },
            ),
        )

        self.assertEqual(response.status_code, 302)
        integrante.refresh_from_db()
        self.assertEqual(integrante.nombre, "Nombre actualizado")
        self.assertEqual(
            AuditoriaProyecto.objects.filter(
                accion=AuditoriaProyecto.Accion.MODIFICAR
            ).count(),
            1,
        )

    def test_eliminacion_conserva_evento_y_snapshots_tras_borrar_actor(self):
        proyecto = self.create_project(creator=self.superuser)
        actor_id = self.superuser.pk
        actor_username = self.superuser.username
        project_id = proyecto.pk
        title = proyecto.titulo
        self.client.force_login(self.superuser)

        response = self.client.post(reverse("proyectos:eliminar", args=[project_id]))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Proyecto.objects.filter(pk=project_id).exists())
        evento = AuditoriaProyecto.objects.get(accion=AuditoriaProyecto.Accion.ELIMINAR)
        self.assertIsNone(evento.proyecto)
        self.assertEqual(evento.proyecto_id_original, project_id)
        self.assertEqual(evento.proyecto_titulo, title)

        self.superuser.delete()
        evento.refresh_from_db()
        self.assertIsNone(evento.actor)
        self.assertEqual(evento.actor_id_original, actor_id)
        self.assertEqual(evento.actor_username, actor_username)


class ProyectoPermisosPublicacionTests(ProyectoTestBase):
    def test_detalle_y_qr_son_publicos_y_ids_ausentes_entregan_404(self):
        proyecto = self.create_project()

        detalle = self.client.get(reverse("proyectos:detalle", args=[proyecto.pk]))
        qr = self.client.get(reverse("proyectos:qr", args=[proyecto.pk]))

        self.assertEqual(detalle.status_code, 200)
        self.assertContains(detalle, proyecto.titulo)
        self.assertEqual(qr.status_code, 200)
        self.assertEqual(qr["Content-Type"], "image/png")
        self.assertEqual(
            self.client.get(reverse("proyectos:detalle", args=[999999])).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse("proyectos:qr", args=[999999])).status_code,
            404,
        )

    def test_superusuario_sin_perfil_puede_editar(self):
        proyecto = self.create_project()
        self.client.force_login(self.superuser)

        response = self.client.post(
            reverse("proyectos:editar", args=[proyecto.pk]),
            self.project_data(titulo="Editado por superusuario"),
        )

        self.assertEqual(response.status_code, 302)
        proyecto.refresh_from_db()
        self.assertEqual(proyecto.titulo, "Editado por superusuario")

    def test_usuario_sin_perfil_no_puede_editar(self):
        proyecto = self.create_project()
        self.client.force_login(self.no_profile)

        response = self.client.get(reverse("proyectos:editar", args=[proyecto.pk]))

        self.assertEqual(response.status_code, 403)

    def test_restricted_no_puede_eliminar(self):
        proyecto = self.create_project()
        self.client.force_login(self.creator)

        response = self.client.post(reverse("proyectos:eliminar", args=[proyecto.pk]))

        self.assertRedirects(response, reverse("Home"))
        self.assertTrue(Proyecto.objects.filter(pk=proyecto.pk).exists())
        self.assertFalse(AuditoriaProyecto.objects.exists())


class RecursoProyectoTests(ProyectoTestBase):
    def test_representacion_usa_campos_existentes(self):
        proyecto = self.create_project()
        solo_archivo = RecursoProyecto(
            proyecto=proyecto,
            titulo="Archivo",
            archivo="proyectos/recurso.pdf",
        )
        solo_enlace = RecursoProyecto(
            proyecto=proyecto,
            titulo="Enlace",
            url="https://example.test",
        )
        ambos = RecursoProyecto(
            proyecto=proyecto,
            titulo="Ambos",
            archivo="proyectos/recurso.pdf",
            url="https://example.test",
        )

        self.assertEqual(str(solo_archivo), "Archivo - archivo")
        self.assertEqual(str(solo_enlace), "Enlace - enlace")
        self.assertEqual(str(ambos), "Ambos - archivo y enlace")
