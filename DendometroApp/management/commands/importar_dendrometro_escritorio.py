"""Importa la configuración y, opcionalmente, lecturas de la app Kivy."""

import json
import math
import sqlite3
from contextlib import closing
from dataclasses import asdict
from datetime import timezone
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_datetime

from DendometroApp.forms import DendrometroForm
from DendometroApp.models import Lectura
from DendometroApp.services.config import AppConfig


class Command(BaseCommand):
    help = "Crea un dendrómetro a partir de dendrometer_config.json; permite importar dendrometer.db sin modificarlo."

    def add_arguments(self, parser):
        parser.add_argument("config_json")
        parser.add_argument("--nombre", required=True)
        parser.add_argument("--ubicacion", default="")
        parser.add_argument("--sqlite", dest="database")

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            original = json.loads(
                Path(options["config_json"]).read_text(encoding="utf-8-sig")
            )
            if not isinstance(original, dict):
                raise ValueError("Se requiere un objeto JSON.")
        except (OSError, ValueError) as exc:
            raise CommandError(
                "No se pudo leer un archivo de configuración válido."
            ) from exc
        data = asdict(AppConfig())
        data.update({k: v for k, v in original.items() if k in data})
        data.update(
            nombre=options["nombre"], ubicacion=options["ubicacion"], activo=True
        )
        form = DendrometroForm(data)
        if not form.is_valid():
            raise CommandError(f"Configuración inválida: {form.errors.as_text()}")
        sensor = form.save()
        count, skipped = 0, 0
        if options["database"]:
            path = Path(options["database"]).resolve()
            if not path.is_file():
                raise CommandError("No existe la base SQLite indicada.")
            try:
                with closing(
                    sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
                ) as source:
                    with closing(
                        source.execute(
                            "SELECT created_at, entry_id, value FROM readings WHERE channel_id=? AND field_id=? ORDER BY created_at",
                            (sensor.channel_id, sensor.field_id),
                        )
                    ) as rows:
                        batch = []
                        for created_at, entry_id, value in rows:
                            try:
                                ts = parse_datetime(created_at)
                                if ts is None or not math.isfinite(float(value)):
                                    raise ValueError()
                                if ts.tzinfo is None:
                                    ts = ts.replace(tzinfo=timezone.utc)
                                batch.append(
                                    Lectura(
                                        dendrometro=sensor,
                                        created_at=ts,
                                        entry_id=entry_id,
                                        value=float(value),
                                    )
                                )
                            except (ValueError, TypeError):
                                skipped += 1
                                continue
                            if len(batch) >= 500:
                                Lectura.objects.bulk_create(
                                    batch, ignore_conflicts=True
                                )
                                count += len(batch)
                                batch = []
                        if batch:
                            Lectura.objects.bulk_create(batch, ignore_conflicts=True)
                            count += len(batch)
            except sqlite3.Error as exc:
                raise CommandError(
                    "La base no contiene la tabla readings esperada de la app de escritorio."
                ) from exc
        self.stdout.write(
            self.style.SUCCESS(
                f"Dendrómetro #{sensor.pk}: {sensor.nombre}. {count} lecturas procesadas; {skipped} omitidas."
            )
        )
        self.stdout.write(
            "La próxima sincronización completará la ventana de ThingSpeak. No se modificaron los archivos originales."
        )
