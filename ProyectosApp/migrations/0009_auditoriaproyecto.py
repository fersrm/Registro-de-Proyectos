import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ProyectosApp", "0008_alter_recursoproyecto_options_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditoriaProyecto",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "accion",
                    models.CharField(
                        choices=[
                            ("CREAR", "Crear"),
                            ("MODIFICAR", "Modificar"),
                            ("ELIMINAR", "Eliminar"),
                        ],
                        max_length=10,
                    ),
                ),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                ("proyecto_id_original", models.PositiveBigIntegerField()),
                ("proyecto_titulo", models.CharField(max_length=200)),
                (
                    "actor_id_original",
                    models.PositiveBigIntegerField(blank=True, null=True),
                ),
                ("actor_username", models.CharField(blank=True, max_length=150)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="eventos_auditoria_proyectos",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "proyecto",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="eventos_auditoria",
                        to="ProyectosApp.proyecto",
                    ),
                ),
            ],
            options={
                "verbose_name": "Auditoría de proyecto",
                "verbose_name_plural": "Auditorías de proyectos",
                "ordering": ["-fecha", "-pk"],
            },
        ),
    ]
