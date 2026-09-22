from __future__ import annotations

from dataclasses import dataclass

DEFAULT_PROJECT_MAINTENANCE_RANGE = "2026-08-26 13:55 |"


@dataclass
class AppConfig:
    # Versión del formato de configuración
    config_version: int = 5

    # ThingSpeak
    channel_id: int = 3363555
    field_id: int = 1
    state_field_id: int = 2
    read_api_key: str = ""
    refresh_seconds: int = 60
    history_days: int = 3
    realtime_hours: int = 6

    # Estado operacional
    sensor_in_maintenance: bool = False

    # Rangos que NO deben interpretarse como comportamiento del árbol.
    # Formato (una línea por rango, UTC):
    #   YYYY-MM-DD HH:MM | YYYY-MM-DD HH:MM
    # El fin puede quedar vacío para un mantenimiento todavía abierto.
    excluded_ranges_utc: str = ""

    # Procesamiento temporal
    aggregate_minutes: int = 30
    aggregate_method: str = "median"  # median | mean
    rolling_window: int = 3
    trend_window_hours: int = 24
    treat_zero_as_invalid: bool = False
    max_jump_um: float = 1000.0

    # Si entre dos puntos agregados pasa más de este tiempo, se inicia una
    # sesión nueva. Esto evita unir/suavizar días o semanas sin información.
    session_gap_minutes: int = 90

    # Cobertura mínima para considerar métricas que requieren tiempo continuo.
    daily_min_coverage_hours: float = 12.0
    trend_min_coverage_hours: float = 18.0

    # Conversión / calibración
    # FIRMWARE ACTUAL: ThingSpeak Field 1 recibe distanciaMM, por lo que la app
    # solo convierte mm -> µm (x1000).
    input_mode: str = "millimeters"
    vex_volts: float = 2.5
    sensor_range_um: float = 11000.0
    ina_gain: float = 1.0
    ina_ref_volts: float = 0.0
    scale_factor: float = 1.0
    offset_um: float = 0.0

    # Alertas. Los valores agronómicos deben calibrarse con datos reales.
    warn_low_um: float = 0.0
    warn_high_um: float = 0.0
    water_deficit_alarm_um: float = 0.0
    daily_contraction_alarm_um: float = 0.0
    recovery_gap_alarm_um: float = 0.0
    negative_trend_alarm_um_day: float = 0.0
    stale_minutes: int = 10
    consecutive_zero_alarm: int = 5
    sensor_reset_warning_um: float = 9000.0

    # Presentación
    show_growth_envelope: bool = True
    show_slow_trend: bool = True

    timezone_name: str = "America/Santiago"
