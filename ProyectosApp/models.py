import os
import uuid

from django.contrib.auth.models import User
from django.db import models

from utils.customer_img import handle_old_project_images


def proyecto_image_path(instance, filename):
    extension = os.path.splitext(filename)[1].lower()
    random_filename = uuid.uuid4().hex
    proyecto_id = instance.pk if instance.pk else "temp"
    return f"proyectos/{proyecto_id}/{random_filename}{extension}"


def recurso_proyecto_path(instance, filename):
    extension = os.path.splitext(filename)[1].lower()
    random_filename = uuid.uuid4().hex
    proyecto_id = instance.proyecto.pk if instance.proyecto_id else "temp"

    return f"proyectos/{proyecto_id}/recursos/{random_filename}{extension}"


class Proyecto(models.Model):
    TRL_CHOICES = [
        ("TRL1", "TRL 1"),
        ("TRL2", "TRL 2"),
        ("TRL3", "TRL 3"),
        ("TRL4", "TRL 4"),
        ("TRL5", "TRL 5"),
        ("TRL6", "TRL 6"),
        ("TRL7", "TRL 7"),
        ("TRL8", "TRL 8"),
    ]

    titulo = models.CharField(max_length=200)

    fecha_inicio = models.DateField()

    empresa_organizacion = models.CharField(max_length=200)

    lugar = models.CharField(max_length=200, default="Inacap")

    descripcion = models.TextField(max_length=1200)

    objetivos = models.TextField(max_length=300)

    trl = models.CharField(max_length=10, choices=TRL_CHOICES, default="TRL1")

    docente_lider = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name="proyectos_liderados"
    )

    imagen_1 = models.ImageField(upload_to=proyecto_image_path, blank=True, null=True)
    imagen_2 = models.ImageField(upload_to=proyecto_image_path, blank=True, null=True)
    imagen_3 = models.ImageField(upload_to=proyecto_image_path, blank=True, null=True)

    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proyectos_creados",
    )

    modificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="proyectos_modificados",
    )

    creado = models.DateTimeField(auto_now_add=True)
    modificado = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if self.pk:
            handle_old_project_images(
                Proyecto,
                self.pk,
                [
                    self.imagen_1,
                    self.imagen_2,
                    self.imagen_3,
                ],
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.titulo


class IntegranteProyecto(models.Model):
    ROLES = [
        ("docente", "Docente"),
        ("estudiante", "Estudiante"),
        ("externo", "Externo"),
    ]

    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="integrantes"
    )

    nombre = models.CharField(max_length=150)

    rol = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.nombre} - {self.get_rol_display()}"

    class Meta:
        ordering = ["rol", "nombre"]


class RecursoProyecto(models.Model):
    proyecto = models.ForeignKey(
        Proyecto, on_delete=models.CASCADE, related_name="recursos"
    )

    titulo = models.CharField(max_length=150)

    archivo = models.FileField(upload_to=recurso_proyecto_path, blank=True, null=True)

    url = models.URLField(blank=True, null=True)

    descripcion = models.CharField(max_length=250, blank=True, null=True)

    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        origenes = []
        if self.archivo:
            origenes.append("archivo")
        if self.url:
            origenes.append("enlace")
        if not origenes:
            return self.titulo
        return f"{self.titulo} - {' y '.join(origenes)}"

    class Meta:
        ordering = [
            "titulo",
        ]


class AuditoriaProyecto(models.Model):
    class Accion(models.TextChoices):
        CREAR = "CREAR", "Crear"
        MODIFICAR = "MODIFICAR", "Modificar"
        ELIMINAR = "ELIMINAR", "Eliminar"

    accion = models.CharField(max_length=10, choices=Accion.choices)
    fecha = models.DateTimeField(auto_now_add=True)
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_auditoria",
    )
    proyecto_id_original = models.PositiveBigIntegerField()
    proyecto_titulo = models.CharField(max_length=200)
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eventos_auditoria_proyectos",
    )
    actor_id_original = models.PositiveBigIntegerField(null=True, blank=True)
    actor_username = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ["-fecha", "-pk"]
        verbose_name = "Auditoría de proyecto"
        verbose_name_plural = "Auditorías de proyectos"

    @classmethod
    def registrar(cls, *, accion, proyecto, actor):
        actor_id = getattr(actor, "pk", None)
        actor_username = actor.get_username() if actor_id else ""
        return cls.objects.create(
            accion=accion,
            proyecto=proyecto,
            proyecto_id_original=proyecto.pk,
            proyecto_titulo=proyecto.titulo,
            actor=actor if actor_id else None,
            actor_id_original=actor_id,
            actor_username=actor_username,
        )

    def __str__(self):
        return f"{self.get_accion_display()}: {self.proyecto_titulo}"
