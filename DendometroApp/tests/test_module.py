from dataclasses import asdict
from datetime import timedelta
from unittest.mock import patch

import pandas as pd
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from DendometroApp.forms import DendrometroForm
from DendometroApp.models import Dendrometro, Lectura
from DendometroApp.services import analysis, sync
from DendometroApp.services.config import AppConfig
from DendometroApp.services.processing import _trend_rate, input_to_um, process_series
from DendometroApp.services.thingspeak import ThingSpeakError
from UsuarioApp.models import Position, Profile


class AnalysisTests(TestCase):
    def raw(self, times, values):
        return pd.DataFrame(
            {
                "created_at": pd.to_datetime(times, utc=True),
                "value": values,
                "entry_id": range(len(values)),
            }
        )

    def cfg(self, **kwargs):
        return AppConfig(
            sensor_in_maintenance=False,
            excluded_ranges_utc=kwargs.pop("excluded_ranges_utc", ""),
            rolling_window=1,
            max_jump_um=kwargs.pop("max_jump_um", 0),
            **kwargs,
        )

    def test_conversion_only_once(self):
        self.assertEqual(
            input_to_um(pd.Series([0.011, 0.5, 11]), self.cfg()).tolist(),
            [11, 500, 11000],
        )

    def test_interval_is_not_session_change(self):
        frame, stats = process_series(
            self.raw(
                ["2026-09-01T10:00Z", "2026-09-01T10:30Z", "2026-09-01T11:00Z"],
                [8, 8.1, 8.4],
            ),
            self.cfg(),
        )
        self.assertAlmostEqual(stats.delta_um, 400)
        self.assertAlmostEqual(analysis.interval_delta(frame, 30), 300)

    def test_missing_interval_has_no_delta(self):
        frame, _ = process_series(
            self.raw(["2026-09-01T10:00Z", "2026-09-01T11:00Z"], [8, 8.1]), self.cfg()
        )
        self.assertIsNone(analysis.interval_delta(frame, 30))

    def test_gap_and_single_point_session(self):
        frame, stats = process_series(
            self.raw(
                ["2026-09-01T10:00Z", "2026-09-01T10:30Z", "2026-09-02T11:00Z"],
                [8, 8.1, 8.4],
            ),
            self.cfg(),
        )
        self.assertEqual(stats.session_count, 2)
        self.assertIsNone(analysis.interval_delta(frame, 30))
        self.assertIsNone(stats.delta_um)
        self.assertTrue((frame.groupby("session_id").relative_um.first() == 0).all())

    def test_short_maintenance_starts_session(self):
        frame, stats = process_series(
            self.raw(
                ["2026-09-01T10:00Z", "2026-09-01T10:35Z", "2026-09-01T11:00Z"],
                [8, 8.1, 8.2],
            ),
            self.cfg(excluded_ranges_utc="2026-09-01 10:40 | 2026-09-01 10:50"),
        )
        self.assertEqual(stats.session_count, 2)
        self.assertEqual(len(frame), 2)
        self.assertIsNone(analysis.interval_delta(frame, 30))

    def test_jump_starts_new_session(self):
        _, stats = process_series(
            self.raw(["2026-09-01T10:00Z", "2026-09-01T10:30Z"], [8, 10]),
            self.cfg(max_jump_um=1000),
        )
        self.assertEqual(stats.session_count, 2)

    def test_daily_amplitude_uses_sensor_timezone(self):
        times = pd.date_range("2026-09-02T02:00Z", periods=5, freq="30min")
        _, utc = process_series(
            self.raw(times, [8, 8.1, 8.2, 8.3, 8.4]),
            self.cfg(daily_min_coverage_hours=2, timezone_name="UTC"),
        )
        _, chile = process_series(
            self.raw(times, [8, 8.1, 8.2, 8.3, 8.4]),
            self.cfg(daily_min_coverage_hours=2, timezone_name="America/Santiago"),
        )
        self.assertEqual(utc.daily_amplitude_um, 400)
        self.assertIsNone(chile.daily_amplitude_um)

    def test_recent_trend_only(self):
        index = pd.date_range("2026-01-01", periods=49, freq="1h", tz="UTC")
        series = pd.Series(list(range(0, 2500, 100)) + [2400.0] * 24, index=index)
        self.assertAlmostEqual(_trend_rate(series, 24, 18), 0, places=6)


class ModuleTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            "admin", password="test", is_superuser=True
        )
        self.reader = User.objects.create_user("reader", password="test")
        self.manager = User.objects.create_user("manager", password="test")
        pos = Position.objects.create(
            user_position="Encargado", permission_code="MANAGER"
        )
        Profile.objects.create(user_FK=self.manager, position_FK=pos, image="")
        self.a = Dendrometro.objects.create(
            nombre="Árbol A", channel_id=101, read_api_key="secret-never-in-json"
        )
        self.b = Dendrometro.objects.create(nombre="Árbol B", channel_id=202)
        self.now = timezone.now().replace(microsecond=0)

    def reading(self, sensor, value=8.5, timestamp=None):
        return Lectura.objects.create(
            dendrometro=sensor,
            created_at=timestamp or self.now,
            value=value,
            entry_id=1,
            estado=1,
        )

    def formdata(self, sensor):
        data = asdict(sensor.config())
        data.update(
            nombre=sensor.nombre,
            ubicacion="",
            descripcion="",
            activo=True,
            read_api_key="",
        )
        return data

    def test_auth_and_manager_permissions(self):
        self.assertEqual(
            self.client.get(reverse("dendometro:datos", args=[self.a.pk])).status_code,
            302,
        )
        self.client.force_login(self.reader)
        for page in ["configuracion", "crear"]:
            self.assertEqual(
                self.client.get(reverse("dendometro:" + page)).status_code, 403
            )
        self.assertEqual(
            self.client.post(
                reverse("dendometro:probar", args=[self.a.pk])
            ).status_code,
            403,
        )
        self.client.force_login(self.manager)
        self.assertEqual(
            self.client.get(reverse("dendometro:configuracion")).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("dendometro:editar", args=[self.a.pk])).status_code,
            200,
        )

    def test_all_pages_render(self):
        self.client.force_login(self.admin)
        for page, args in [
            ("listado", []),
            ("configuracion", []),
            ("crear", []),
            ("editar", [self.a.pk]),
            ("visualizacion", [self.a.pk]),
        ]:
            result = self.client.get(reverse("dendometro:" + page, args=args))
            self.assertEqual(result.status_code, 200, page)
            self.assertNotContains(result, self.a.read_api_key)

    def test_no_sensor_or_key_leakage(self):
        self.reading(self.a, 8)
        self.reading(self.b, 10)
        self.client.force_login(self.reader)
        response = self.client.get(reverse("dendometro:datos", args=[self.a.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.a.read_api_key)
        self.assertEqual(response.json()["metrics"]["latest_signal_um"], 8000)
        self.assertEqual(response.json()["raw_count"], 1)
        export = self.client.get(
            reverse("dendometro:exportar", args=[self.a.pk, "crudo"])
        )
        self.assertContains(export, "8000")
        self.assertNotContains(export, "10000")

    def test_csrf_required_and_get_does_not_sync(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.admin)
        url = reverse("dendometro:sincronizar", args=[self.a.pk])
        self.assertEqual(client.post(url).status_code, 403)
        self.assertEqual(client.get(url).status_code, 405)

    def test_config_independent_and_keeps_key(self):
        values = self.formdata(self.a)
        values["scale_factor"] = 2
        form = DendrometroForm(values, instance=self.a)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.a.refresh_from_db()
        self.b.refresh_from_db()
        self.assertEqual(self.a.config().scale_factor, 2)
        self.assertEqual(self.b.config().scale_factor, 1)
        self.assertEqual(self.a.read_api_key, "secret-never-in-json")

    def test_clear_key(self):
        values = self.formdata(self.a)
        values["borrar_clave"] = True
        form = DendrometroForm(values, instance=self.a)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.a.refresh_from_db()
        self.assertEqual(self.a.read_api_key, "")

    def test_reject_mixed_source_after_readings(self):
        self.reading(self.a)
        values = self.formdata(self.a)
        values["channel_id"] = 999
        form = DendrometroForm(values, instance=self.a)
        self.assertFalse(form.is_valid())
        self.assertIn("channel_id", form.errors)

    def test_invalid_configuration(self):
        values = self.formdata(self.a)
        values.update(
            excluded_ranges_utc="bad range",
            timezone_name="Mars/Space",
            ina_gain=0,
            trend_min_coverage_hours=30,
        )
        form = DendrometroForm(values, instance=self.a)
        self.assertFalse(form.is_valid())
        for field in [
            "excluded_ranges_utc",
            "timezone_name",
            "ina_gain",
            "trend_min_coverage_hours",
        ]:
            self.assertIn(field, form.errors)

    def test_maintenance_creates_range_and_hides_metrics(self):
        values = self.formdata(self.a)
        values["sensor_in_maintenance"] = True
        form = DendrometroForm(values, instance=self.a)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.a.refresh_from_db()
        self.assertIn("|", self.a.config().excluded_ranges_utc)
        self.reading(self.a)
        data = analysis.payload(self.a)
        self.assertEqual(data["metrics"]["alert_level"], "MANTENIMIENTO")
        self.assertIsNone(data["metrics"]["interval_delta_um"])
        self.assertEqual(data["raw_count"], 1)

    def test_stale_signal_even_after_successful_download(self):
        self.reading(self.a, timestamp=self.now - timedelta(hours=2))
        data = analysis.payload(self.a)
        self.assertEqual(data["metrics"]["alert_level"], "DATOS ATRASADOS")

    @patch("DendometroApp.services.sync.fetch")
    def test_sync_repeated_no_duplicates_and_isolated(self, fetch):
        fetch.return_value = (
            [dict(created_at=self.now, entry_id=1, value=8.5, estado=1)],
            1,
            0,
        )
        job = sync.start(self.a)
        while job.estado == "pendiente":
            job = sync.step(job)
        self.assertEqual(job.estado, "completa")
        self.assertEqual(self.a.lecturas.count(), 1)
        self.assertEqual(self.b.lecturas.count(), 0)
        job = sync.start(self.a, force=True)
        while job.estado == "pendiente":
            job = sync.step(job)
        self.assertEqual(self.a.lecturas.count(), 1)

    @patch("DendometroApp.services.sync.fetch")
    def test_full_page_splits_without_claiming_completion(self, fetch):
        fetch.return_value = ([], 8000, 0)
        job = sync.start(self.a)
        n = len(job.rangos)
        job = sync.step(job)
        self.assertEqual(len(job.rangos), n + 1)
        self.assertEqual(job.segundos_completos, 0)
        self.assertEqual(job.estado, "pendiente")

    @patch(
        "DendometroApp.services.sync.fetch",
        side_effect=ThingSpeakError("No hay conexión."),
    )
    def test_failure_preserves_data_and_retries(self, fetch):
        self.reading(self.a)
        job = sync.step(sync.start(self.a))
        self.assertEqual(job.estado, "error")
        self.assertEqual(self.a.lecturas.count(), 1)
        new = sync.start(self.a)
        self.assertNotEqual(job.pk, new.pk)

    @patch("DendometroApp.services.sync.fetch")
    def test_two_clients_share_job_and_lease(self, fetch):
        first = sync.start(self.a)
        second = sync.start(self.a)
        self.assertEqual(first.pk, second.pk)
        first.lease_until = timezone.now() + timedelta(seconds=30)
        first.save()
        sync.step(second)
        fetch.assert_not_called()

    def test_job_cannot_be_used_for_another_sensor(self):
        job = sync.start(self.a)
        self.client.force_login(self.reader)
        response = self.client.post(
            reverse("dendometro:paso", args=[self.b.pk, job.pk])
        )
        self.assertEqual(response.status_code, 404)

    def test_import_desktop_configuration_and_sqlite(self):
        import json
        import sqlite3
        import tempfile
        from contextlib import closing
        from io import StringIO
        from pathlib import Path

        from django.core.management import call_command

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cfg = asdict(
                AppConfig(
                    channel_id=123, sensor_in_maintenance=False, excluded_ranges_utc=""
                )
            )
            (root / "config.json").write_text(json.dumps(cfg))
            with closing(sqlite3.connect(root / "desktop.db")) as conn:
                conn.execute(
                    "CREATE TABLE readings (channel_id INTEGER, field_id INTEGER, created_at TEXT, entry_id INTEGER, value REAL)"
                )
                conn.execute(
                    "INSERT INTO readings VALUES (?, ?, ?, ?, ?)",
                    (123, 1, self.now.isoformat(), 99, 8.5),
                )
                conn.execute(
                    "INSERT INTO readings VALUES (?, ?, ?, ?, ?)",
                    (999, 1, self.now.isoformat(), 99, 9.9),
                )
                conn.commit()
            before = (root / "desktop.db").read_bytes()
            call_command(
                "importar_dendrometro_escritorio",
                str(root / "config.json"),
                nombre="Importado",
                database=str(root / "desktop.db"),
                stdout=StringIO(),
            )
            imported = Dendrometro.objects.get(nombre="Importado")
            self.assertEqual(imported.lecturas.count(), 1)
            self.assertEqual(imported.lecturas.first().value, 8.5)
            self.assertEqual((root / "desktop.db").read_bytes(), before)

    @patch("DendometroApp.services.thingspeak.requests.get")
    def test_remote_parser_discards_nan_and_uses_selected_state(self, get):
        from DendometroApp.services.thingspeak import fetch

        self.a.state_field_id = 4
        get.return_value.status_code = 200
        get.return_value.json.return_value = {
            "channel": {"field1": "mm"},
            "feeds": [
                {
                    "created_at": self.now.isoformat(),
                    "entry_id": 1,
                    "field1": "8.5",
                    "field4": "1",
                },
                {"created_at": self.now.isoformat(), "entry_id": 2, "field1": "NaN"},
                {"created_at": "bad", "entry_id": 3, "field1": "9"},
            ],
        }
        rows, count, skipped = fetch(self.a)
        self.assertEqual((count, skipped, len(rows)), (3, 2, 1))
        self.assertEqual(rows[0]["estado"], 1)
        self.assertTrue(
            get.call_args.args[0].startswith("https://api.thingspeak.com/channels/101/")
        )

    def test_zero_diagnostic_even_when_zeros_excluded(self):
        self.a.configuracion.update(
            treat_zero_as_invalid=True, consecutive_zero_alarm=3
        )
        self.a.save()
        for i in range(3):
            self.reading(
                self.a, value=0, timestamp=self.now - timedelta(seconds=i * 20)
            )
        result = analysis.payload(self.a)
        self.assertEqual(result["metrics"]["alert_level"], "REVISAR SENSOR")
        self.assertIsNone(result["metrics"]["interval_delta_um"])
