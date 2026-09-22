import math
from dataclasses import asdict
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pandas as pd
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Dendrometro
from .services.config import AppConfig
from .services.processing import normalize_excluded_ranges_text

# Grupo, etiqueta, ayuda, mínimo, máximo. Se renderizan con crispy_tailwind.
SPECS = {
    "refresh_seconds": (
        "ThingSpeak",
        "Refresco automático (s)",
        "Solo mientras esta página esté abierta. Mínimo 15 s.",
        15,
        86400,
    ),
    "history_days": (
        "ThingSpeak",
        "Ventana de análisis (días)",
        "Historial a descargar y analizar. Ampliarlo puede requerir una carga inicial más larga.",
        1,
        365,
    ),
    "realtime_hours": (
        "ThingSpeak",
        "Ventana de tiempo real (horas)",
        "Lecturas crudas recientes para diagnóstico.",
        1,
        168,
    ),
    "aggregate_minutes": (
        "Tratamiento de la serie",
        "Intervalo de análisis (min)",
        "30 min por defecto. El cambio compara los dos últimos intervalos consecutivos.",
        1,
        1440,
    ),
    "aggregate_method": (
        "Tratamiento de la serie",
        "Agregación",
        "Mediana: reduce el efecto de valores aislados. Media: promedio aritmético.",
        None,
        None,
    ),
    "rolling_window": (
        "Tratamiento de la serie",
        "Mediana móvil (puntos)",
        "Suavizado centrado, independiente por sesión. Los últimos puntos pueden cambiar al llegar datos.",
        1,
        121,
    ),
    "trend_window_hours": (
        "Tratamiento de la serie",
        "Ventana de tendencia lenta (h)",
        "Ventana utilizada para la curva lenta y su pendiente.",
        1,
        168,
    ),
    "max_jump_um": (
        "Tratamiento de la serie",
        "Salto máximo entre intervalos (µm)",
        "Un salto superior abre otra sesión. 0 desactiva este corte.",
        0,
        None,
    ),
    "session_gap_minutes": (
        "Tratamiento de la serie",
        "Nueva sesión tras un hueco mayor a (min)",
        "No representa necesariamente una desconexión física.",
        1,
        10080,
    ),
    "daily_min_coverage_hours": (
        "Tratamiento de la serie",
        "Cobertura mínima amplitud / recuperación (h)",
        "Extensión temporal mínima entre datos; no garantiza muestras en todos los minutos.",
        0,
        24,
    ),
    "trend_min_coverage_hours": (
        "Tratamiento de la serie",
        "Cobertura mínima tendencia (h)",
        "Si no alcanza esta duración, la pendiente muestra —.",
        0,
        168,
    ),
    "treat_zero_as_invalid": (
        "Tratamiento de la serie",
        "Excluir ceros exactos del análisis",
        "Las lecturas crudas se conservan.",
        None,
        None,
    ),
    "show_growth_envelope": (
        "Presentación",
        "Mostrar máximo / envolvente",
        "Máximo acumulado por sesión de la curva suavizada.",
        None,
        None,
    ),
    "show_slow_trend": (
        "Presentación",
        "Mostrar tendencia lenta",
        "Curva lenta en el gráfico relativo.",
        None,
        None,
    ),
    "timezone_name": (
        "Presentación",
        "Zona horaria",
        "Ej.: America/Santiago. Define las fechas del gráfico y el día de la amplitud.",
        None,
        None,
    ),
    "input_mode": (
        "Conversión y calibración",
        "Unidad recibida",
        "Firmware ESP32 entregado: millimeters (mm → µm, una sola vez).",
        None,
        None,
    ),
    "vex_volts": (
        "Conversión y calibración",
        "Excitación del dendrómetro (V)",
        "Solo para modos de voltaje.",
        0.000001,
        None,
    ),
    "sensor_range_um": (
        "Conversión y calibración",
        "Rango del sensor (µm)",
        "11 mm = 11000 µm. Conversión de voltaje.",
        0.000001,
        None,
    ),
    "ina_gain": (
        "Conversión y calibración",
        "Ganancia INA333",
        "Solo para voltaje post-INA333.",
        0.000001,
        None,
    ),
    "ina_ref_volts": (
        "Conversión y calibración",
        "Referencia INA333 (V)",
        "Solo para voltaje post-INA333.",
        None,
        None,
    ),
    "scale_factor": (
        "Conversión y calibración",
        "Factor de calibración",
        "Se aplica después de convertir a µm. Puede ser negativo para invertir el sentido.",
        None,
        None,
    ),
    "offset_um": (
        "Conversión y calibración",
        "Offset de calibración (µm)",
        "Corrección aditiva posterior a la escala.",
        None,
        None,
    ),
    "warn_low_um": (
        "Alertas",
        "Umbral bajo de cambio acumulado (µm)",
        "Negativo; 0 desactiva. Mantiene el criterio de sesión de la app original.",
        None,
        0,
    ),
    "warn_high_um": (
        "Alertas",
        "Umbral alto de cambio acumulado (µm)",
        "Positivo; 0 desactiva. No se refiere a la tarjeta del último intervalo.",
        0,
        None,
    ),
    "water_deficit_alarm_um": (
        "Alertas",
        "Déficit vs. máximo (µm)",
        "Negativo; 0 desactiva.",
        None,
        0,
    ),
    "daily_contraction_alarm_um": (
        "Alertas",
        "Amplitud diaria alta (µm)",
        "Positivo; 0 desactiva.",
        0,
        None,
    ),
    "recovery_gap_alarm_um": (
        "Alertas",
        "Falta de recuperación 24 h (µm)",
        "Magnitud positiva del déficit permitido; 0 desactiva.",
        0,
        None,
    ),
    "negative_trend_alarm_um_day": (
        "Alertas",
        "Tendencia negativa (µm/día)",
        "Magnitud positiva del descenso; 0 desactiva.",
        0,
        None,
    ),
    "stale_minutes": (
        "Alertas",
        "Aviso sin datos tras (min)",
        "Se calcula desde la última lectura recibida, no desde la última consulta.",
        1,
        10080,
    ),
    "consecutive_zero_alarm": (
        "Alertas",
        "Aviso tras N ceros consecutivos",
        "0 desactiva.",
        0,
        1000,
    ),
    "sensor_reset_warning_um": (
        "Alertas",
        "Aviso de reajuste (µm)",
        "Posición absoluta elevada del sensor; 0 desactiva.",
        0,
        None,
    ),
    "sensor_in_maintenance": (
        "Mantenimiento",
        "Sensor en mantenimiento / pruebas",
        "Pausa las alarmas y oculta las métricas actuales. Inicia/cierra un rango UTC al guardar.",
        None,
        None,
    ),
    "excluded_ranges_utc": (
        "Mantenimiento",
        "Períodos excluidos (UTC)",
        "Una línea: 2026-09-20 13:00 | 2026-09-20 15:00. Fin vacío = sigue abierto.",
        None,
        None,
    ),
}


class DendrometroForm(forms.ModelForm):
    borrar_clave = forms.BooleanField(
        required=False, label="Eliminar la Read API Key guardada (canal público)"
    )

    class Meta:
        model = Dendrometro
        fields = [
            "nombre",
            "ubicacion",
            "descripcion",
            "activo",
            "channel_id",
            "field_id",
            "state_field_id",
            "read_api_key",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 2}),
            "read_api_key": forms.PasswordInput(render_value=False),
        }
        help_texts = {
            "read_api_key": "Dejar vacío conserva la clave actual. Nunca se envía a la visualización.",
            "activo": "Desactivar detiene la descarga; conserva el historial.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cfg = asdict(self.instance.config() if self.instance.pk else AppConfig())
        choices = {
            "aggregate_method": [("median", "Mediana"), ("mean", "Media")],
            "input_mode": [
                ("millimeters", "Milímetros (firmware actual)"),
                ("micrometers", "Micrómetros"),
                ("voltage_sensor", "Voltaje del sensor"),
                ("voltage_post_ina", "Voltaje post-INA333"),
            ],
        }
        for name, (group, label, help_text, low, high) in SPECS.items():
            value = cfg[name]
            opts = dict(label=label, help_text=help_text, initial=value)
            if name in choices:
                field = forms.ChoiceField(choices=choices[name], **opts)
            elif isinstance(value, bool):
                field = forms.BooleanField(required=False, **opts)
            elif isinstance(value, int):
                field = forms.IntegerField(min_value=low, max_value=high, **opts)
            elif isinstance(value, float):
                field = forms.FloatField(min_value=low, max_value=high, **opts)
            else:
                if name == "excluded_ranges_utc":
                    opts.update(
                        required=False, widget=forms.Textarea(attrs={"rows": 5})
                    )
                field = forms.CharField(**opts)
            self.fields[name] = field
        if self.instance.pk:
            self.initial["read_api_key"] = ""
        self.groups = []
        for title, names in [
            ("Identificación", ["nombre", "ubicacion", "descripcion", "activo"]),
            (
                "ThingSpeak",
                [
                    "channel_id",
                    "field_id",
                    "state_field_id",
                    "read_api_key",
                    "borrar_clave",
                ],
            ),
        ]:
            self.groups.append(
                (title, names + [n for n, spec in SPECS.items() if spec[0] == title])
            )
        for title in [
            "Tratamiento de la serie",
            "Conversión y calibración",
            "Mantenimiento",
            "Alertas",
            "Presentación",
        ]:
            self.groups.append(
                (title, [n for n, spec in SPECS.items() if spec[0] == title])
            )

    def sections(self):
        return [(title, [self[name] for name in names]) for title, names in self.groups]

    def clean(self):
        data = super().clean()
        for name, value in data.items():
            if isinstance(value, float) and not math.isfinite(value):
                self.add_error(name, "Ingresa un número finito.")
        if data.get("field_id") == data.get("state_field_id"):
            self.add_error(
                "state_field_id", "El estado debe usar otro campo de ThingSpeak."
            )
        if data.get("scale_factor") == 0:
            self.add_error("scale_factor", "El factor no puede ser cero.")
        if data.get("session_gap_minutes", 90) < data.get("aggregate_minutes", 30):
            self.add_error(
                "session_gap_minutes",
                "Debe ser igual o mayor que el intervalo de análisis.",
            )
        if data.get("trend_min_coverage_hours", 18) > data.get(
            "trend_window_hours", 24
        ):
            self.add_error(
                "trend_min_coverage_hours", "No puede superar la ventana de tendencia."
            )
        try:
            ZoneInfo(data.get("timezone_name", ""))
        except (ValueError, ZoneInfoNotFoundError):
            self.add_error(
                "timezone_name", "Zona horaria inválida. Ej.: America/Santiago."
            )
        text = data.get("excluded_ranges_utc", "")
        for line in text.splitlines():
            if not line.strip() or line.strip().startswith("#"):
                continue
            try:
                start, end = line.split("|")
                start = pd.to_datetime(start.strip(), utc=True, errors="raise")
                if pd.isna(start):
                    raise ValueError()
                if end.strip():
                    end = pd.to_datetime(end.strip(), utc=True, errors="raise")
                    if pd.isna(end) or end <= start:
                        raise ValueError()
            except (ValueError, TypeError):
                self.add_error(
                    "excluded_ranges_utc",
                    "Cada línea requiere inicio | fin, fechas válidas y fin posterior al inicio.",
                )
                break
        if self.instance.pk:
            old = Dendrometro.objects.get(pk=self.instance.pk)
            if old.lecturas.exists():
                for key in ("channel_id", "field_id", "state_field_id"):
                    if data.get(key) != getattr(old, key):
                        self.add_error(
                            key,
                            "Este sensor ya tiene lecturas. Crea otro dendrómetro para cambiar el origen sin mezclar historiales.",
                        )
            if old.sincronizaciones.filter(
                estado="pendiente", lease_until__gt=timezone.now()
            ).exists():
                raise ValidationError(
                    "Hay una descarga en curso. Espera a que termine este paso y vuelve a guardar."
                )
            if not data.get("read_api_key") and not data.get("borrar_clave"):
                data["read_api_key"] = old.read_api_key
        if data.get("borrar_clave"):
            data["read_api_key"] = ""
        return data

    @transaction.atomic
    def save(self, commit=True):
        obj = super().save(commit=False)
        config = {n: self.cleaned_data[n] for n in SPECS}
        text = normalize_excluded_ranges_text(config["excluded_ranges_utc"])
        now = timezone.now().strftime("%Y-%m-%d %H:%M")
        lines = text.splitlines()
        has_open = any(not line.split("|")[1].strip() for line in lines)
        if config["sensor_in_maintenance"] and not has_open:
            lines.append(f"{now} |")
        if not config["sensor_in_maintenance"]:
            lines = [
                line + " " + now if not line.split("|")[1].strip() else line
                for line in lines
            ]
        config["excluded_ranges_utc"] = normalize_excluded_ranges_text("\n".join(lines))
        obj.configuracion = config
        obj.revision += 1
        if commit:
            obj.save()
            obj.sincronizaciones.filter(estado="pendiente").update(
                estado="cancelada", error="Configuración actualizada."
            )
        return obj
