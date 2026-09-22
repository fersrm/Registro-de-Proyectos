import uuid
from dataclasses import asdict

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from .services.config import AppConfig


def default_config():
    cfg = asdict(AppConfig())
    for key in ("channel_id", "field_id", "state_field_id", "read_api_key"):
        cfg.pop(key)
    return cfg


class Dendrometro(models.Model):
    nombre = models.CharField("Nombre", max_length=100)
    ubicacion = models.CharField("Ubicación / árbol", max_length=200, blank=True)
    descripcion = models.TextField("Descripción", blank=True)
    activo = models.BooleanField("Habilitado para sincronizar", default=True)
    channel_id = models.PositiveIntegerField(
        "Channel ID", validators=[MinValueValidator(1)]
    )
    field_id = models.PositiveSmallIntegerField(
        "Campo de señal",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
    )
    state_field_id = models.PositiveSmallIntegerField(
        "Campo de estado",
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
    )
    read_api_key = models.CharField("Read API Key", max_length=128, blank=True)
    configuracion = models.JSONField(default=default_config)
    revision = models.PositiveIntegerField(default=1)
    sincronizado_desde = models.DateTimeField(null=True, blank=True)
    ultima_sincronizacion = models.DateTimeField(null=True, blank=True)
    ultimo_error = models.CharField(max_length=250, blank=True)
    creado = models.DateTimeField(default=timezone.now)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre", "pk"]
        verbose_name = "Dendrómetro"
        verbose_name_plural = "Dendrómetros"

    def __str__(self):
        return self.nombre

    def config(self):
        values = default_config()
        values.update({k: v for k, v in self.configuracion.items() if k in values})
        return AppConfig(
            **values,
            channel_id=self.channel_id,
            field_id=self.field_id,
            state_field_id=self.state_field_id,
            read_api_key=self.read_api_key,
        )


class Lectura(models.Model):
    dendrometro = models.ForeignKey(
        Dendrometro, on_delete=models.CASCADE, related_name="lecturas"
    )
    created_at = models.DateTimeField()
    entry_id = models.BigIntegerField(null=True)
    value = models.FloatField()
    estado = models.FloatField(null=True)

    class Meta:
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["dendrometro", "created_at"], name="dendro_lectura_unica"
            )
        ]
        indexes = [
            models.Index(
                fields=["dendrometro", "created_at"], name="dendro_sensor_fecha"
            )
        ]


class Sincronizacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dendrometro = models.ForeignKey(
        Dendrometro, on_delete=models.CASCADE, related_name="sincronizaciones"
    )
    revision = models.PositiveIntegerField()
    estado = models.CharField(max_length=12, default="pendiente")
    rangos = models.JSONField(default=list)
    inicio = models.DateTimeField()
    fin = models.DateTimeField()
    segundos_completos = models.FloatField(default=0)
    registros = models.PositiveIntegerField(default=0)
    omitidos = models.PositiveIntegerField(default=0)
    error = models.CharField(max_length=250, blank=True)
    lease_until = models.DateTimeField(null=True)
    lease_token = models.UUIDField(null=True)
    actualizado = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["dendrometro"],
                condition=models.Q(estado="pendiente"),
                name="dendro_sync_activa_unica",
            )
        ]
