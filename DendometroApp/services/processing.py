from __future__ import annotations

from dataclasses import dataclass
import re

import numpy as np
import pandas as pd

from .config import AppConfig


@dataclass
class SeriesStats:
    # Última señal recibida (incluye mantenimiento/pruebas)
    latest_signal_um: float | None = None
    latest_signal_timestamp: pd.Timestamp | None = None

    # Última lectura cruda perteneciente a un período operativo
    last_operational_raw_um: float | None = None
    last_operational_raw_timestamp: pd.Timestamp | None = None

    # Último intervalo procesado válido para interpretar el árbol
    latest_um: float | None = None
    last_valid_timestamp: pd.Timestamp | None = None

    # Métricas de la ÚLTIMA sesión operativa válida
    delta_um: float | None = None
    daily_amplitude_um: float | None = None
    water_deficit_um: float | None = None
    recovery_gap_um: float | None = None
    trend_rate_um_day: float | None = None

    max_detected_jump_um: float | None = None
    last_jump_um: float | None = None
    last_jump_timestamp: pd.Timestamp | None = None
    session_count: int = 0
    excluded_count: int = 0
    valid_analysis_points: int = 0

    alert_level: str = "SIN DATOS"
    alert_message: str = "Aún no hay datos."


@dataclass
class ExclusionRange:
    start: pd.Timestamp
    end: pd.Timestamp | None
    label: str = "MANTENIMIENTO"


def input_to_um(values: pd.Series, cfg: AppConfig) -> pd.Series:
    """Convierte la señal recibida a desplazamiento del DC1 en µm.

    Firmware actual:
        ThingSpeak Field 1 = distanciaMM
        µm = mm * 1000

    Los modos de voltaje quedan solo por compatibilidad con otros firmwares.
    """
    values = pd.to_numeric(values, errors="coerce").astype(float)
    mode = (cfg.input_mode or "millimeters").strip().lower()

    if mode == "millimeters":
        um = values * 1000.0
    elif mode == "micrometers":
        um = values.copy()
    else:
        if mode == "voltage_post_ina":
            gain = cfg.ina_gain if abs(cfg.ina_gain) > 1e-12 else 1.0
            sensor_v = (values - cfg.ina_ref_volts) / gain
        elif mode == "voltage_sensor":
            sensor_v = values
        else:
            # Modo desconocido: en este proyecto es más seguro tratarlo como mm
            # que convertirlo por segunda vez como voltaje.
            um = values * 1000.0
            return um * cfg.scale_factor + cfg.offset_um

        vex = cfg.vex_volts if abs(cfg.vex_volts) > 1e-12 else 2.5
        um = (sensor_v / vex) * cfg.sensor_range_um

    return um * cfg.scale_factor + cfg.offset_um


voltage_to_um = input_to_um  # compatibilidad v2


def _parse_timestamp_utc(text: str) -> pd.Timestamp | None:
    text = str(text or "").strip()
    if not text:
        return None
    try:
        ts = pd.to_datetime(text, utc=True, errors="raise")
        return pd.Timestamp(ts)
    except Exception:
        return None


def parse_excluded_ranges(text: str) -> list[ExclusionRange]:
    """Lee rangos UTC, uno por línea.

    Formatos aceptados:
        2026-08-26 13:55 | 2026-08-27 10:00
        2026-08-26 13:55 |            # abierto hasta ahora
        2026-08-26T13:55Z -> 2026-08-27T10:00Z
    """
    ranges: list[ExclusionRange] = []
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = re.split(r"\s*(?:\||->|→)\s*", line, maxsplit=1)
        start = _parse_timestamp_utc(parts[0])
        end = _parse_timestamp_utc(parts[1]) if len(parts) > 1 else None
        if start is None:
            continue
        if end is not None and end < start:
            start, end = end, start
        ranges.append(ExclusionRange(start=start, end=end))
    return ranges


def normalize_excluded_ranges_text(text: str) -> str:
    """Devuelve rangos UTC ordenados, sin duplicados ni períodos vacíos.

    Además une rangos superpuestos. Esto evita que acciones repetidas sobre el
    switch de mantenimiento acumulen líneas idénticas en la configuración.
    """
    parsed = sorted(
        parse_excluded_ranges(text),
        key=lambda item: (
            item.start,
            pd.Timestamp.max.tz_localize("UTC") if item.end is None else item.end,
        ),
    )

    cleaned: list[ExclusionRange] = []
    seen: set[tuple[int, int | None]] = set()
    for item in parsed:
        # Un inicio y fin iguales no describen un período útil y normalmente
        # aparecen al pulsar iniciar/finalizar en el mismo minuto.
        if item.end is not None and item.end == item.start:
            continue

        key = (item.start.value, None if item.end is None else item.end.value)
        if key in seen:
            continue
        seen.add(key)

        if cleaned and cleaned[-1].end is None:
            # Un rango abierto anterior ya contiene cualquier rango posterior.
            continue

        if cleaned and cleaned[-1].end is not None and item.start <= cleaned[-1].end:
            previous = cleaned[-1]
            if item.end is None:
                previous.end = None
            elif item.end > previous.end:
                previous.end = item.end
            continue

        cleaned.append(ExclusionRange(item.start, item.end, item.label))

    lines: list[str] = []
    for item in cleaned:
        start = item.start.strftime("%Y-%m-%d %H:%M")
        end = "" if item.end is None else item.end.strftime("%Y-%m-%d %H:%M")
        lines.append(f"{start} | {end}".rstrip())
    return "\n".join(lines)


def annotate_raw_series(raw_df: pd.DataFrame, cfg: AppConfig) -> pd.DataFrame:
    """Añade µm y marca qué lecturas se excluyen del análisis fisiológico.

    La lectura cruda SIEMPRE se conserva. La exclusión solo afecta al análisis.
    """
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(
            columns=[
                "created_at",
                "value",
                "entry_id",
                "um",
                "analysis_excluded",
                "exclusion_reason",
            ]
        )

    df = raw_df.copy()
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
    df["raw"] = pd.to_numeric(df.get("value"), errors="coerce")
    df = df.dropna(subset=["created_at", "raw"]).sort_values("created_at")
    if df.empty:
        return df

    df["um"] = input_to_um(df["raw"], cfg)
    df["analysis_excluded"] = False
    df["exclusion_reason"] = ""

    if cfg.treat_zero_as_invalid:
        zero_mask = df["raw"].abs() < 1e-12
        df.loc[zero_mask, "analysis_excluded"] = True
        df.loc[zero_mask, "exclusion_reason"] = "CERO_INVALIDO"

    now = pd.Timestamp.now(tz="UTC")
    for exclusion in parse_excluded_ranges(cfg.excluded_ranges_utc):
        end = exclusion.end if exclusion.end is not None else now
        mask = (df["created_at"] >= exclusion.start) & (df["created_at"] <= end)
        df.loc[mask, "analysis_excluded"] = True
        df.loc[mask, "exclusion_reason"] = exclusion.label

    return df


def _assign_sessions(index: pd.DatetimeIndex, gap_minutes: int) -> pd.Series:
    if len(index) == 0:
        return pd.Series(dtype="int64", index=index)
    gaps = pd.Series(index, index=index).diff() > pd.Timedelta(
        minutes=max(1, int(gap_minutes))
    )
    session_ids = gaps.fillna(False).cumsum().astype(int) + 1
    session_ids.index = index
    return session_ids


def _smooth_by_session(proc: pd.DataFrame, window: int) -> pd.Series:
    pieces = []
    for _, group in proc.groupby("session_id", sort=True):
        sm = (
            group["um"]
            .rolling(window=max(1, int(window)), min_periods=1, center=True)
            .median()
        )
        pieces.append(sm)
    return pd.concat(pieces).sort_index() if pieces else pd.Series(dtype=float)


def _relative_by_session(proc: pd.DataFrame, column: str) -> pd.Series:
    result = pd.Series(index=proc.index, dtype=float)
    for _, group in proc.groupby("session_id", sort=True):
        baseline = float(group[column].iloc[0])
        result.loc[group.index] = group[column] - baseline
    return result


def _trend_column(proc: pd.DataFrame, cfg: AppConfig) -> pd.Series:
    result = pd.Series(index=proc.index, dtype=float)
    minutes = max(1, int(cfg.aggregate_minutes))
    trend_points = max(2, round(max(1, cfg.trend_window_hours) * 60 / minutes))
    min_points = max(2, min(4, trend_points))

    for _, group in proc.groupby("session_id", sort=True):
        trend = (
            group["relative_um"]
            .rolling(
                window=trend_points,
                min_periods=min_points,
            )
            .median()
        )
        # No interpolamos al principio/final ni a través de huecos: si no hay
        # cobertura suficiente, la tendencia simplemente queda sin valor.
        result.loc[group.index] = trend
    return result


def _trend_rate(
    series: pd.Series,
    window_hours: float,
    min_coverage_hours: float,
) -> float | None:
    """Calcula la pendiente solo en la ventana reciente configurada."""
    sample = series.dropna()
    if len(sample) < 2:
        return None

    end = sample.index[-1]
    start = end - pd.Timedelta(hours=max(1.0, float(window_hours)))
    sample = sample.loc[sample.index >= start]
    if len(sample) < 2:
        return None

    span_h = (sample.index[-1] - sample.index[0]).total_seconds() / 3600.0
    if span_h < max(0.0, float(min_coverage_hours)):
        return None

    x_days = (sample.index - sample.index[0]).total_seconds() / 86400.0
    if float(np.ptp(x_days)) <= 1e-12:
        return None
    slope, _ = np.polyfit(
        np.asarray(x_days, dtype=float), sample.to_numpy(dtype=float), 1
    )
    return float(slope)


def _latest_signal_from_annotated(
    annotated: pd.DataFrame,
) -> tuple[float | None, pd.Timestamp | None]:
    if annotated.empty:
        return None, None
    row = annotated.iloc[-1]
    return float(row["um"]), pd.Timestamp(row["created_at"])


def process_series(
    raw_df: pd.DataFrame, cfg: AppConfig
) -> tuple[pd.DataFrame, SeriesStats]:
    annotated = annotate_raw_series(raw_df, cfg)
    latest_signal, latest_signal_ts = _latest_signal_from_annotated(annotated)

    stats = SeriesStats(
        latest_signal_um=latest_signal,
        latest_signal_timestamp=latest_signal_ts,
    )

    if annotated.empty:
        if cfg.sensor_in_maintenance:
            stats.alert_level = "MANTENIMIENTO"
            stats.alert_message = "Sensor marcado en mantenimiento; alarmas pausadas."
        return pd.DataFrame(), stats

    stats.excluded_count = int(annotated["analysis_excluded"].sum())

    # Solo estas filas representan períodos operativos válidos para el árbol.
    valid = annotated.loc[~annotated["analysis_excluded"]].copy()
    if not valid.empty:
        last_operational = valid.iloc[-1]
        stats.last_operational_raw_um = float(last_operational["um"])
        stats.last_operational_raw_timestamp = pd.Timestamp(
            last_operational["created_at"]
        )

    if valid.empty:
        stats.alert_level = (
            "MANTENIMIENTO" if cfg.sensor_in_maintenance else "SIN DATOS VÁLIDOS"
        )
        stats.alert_message = (
            "Las lecturas se conservan, pero el período actual está excluido del análisis."
            if cfg.sensor_in_maintenance
            else "No hay lecturas operativas válidas dentro de la ventana seleccionada."
        )
        return pd.DataFrame(), stats

    valid = valid.set_index("created_at").sort_index()

    # 1) Agregación primero. La señal cruda puede oscilar mucho; el filtro de
    # salto se aplica a las MEDIANAS/PROMEDIOS del intervalo, no a cada muestra.
    minutes = max(1, int(cfg.aggregate_minutes))
    rule = f"{minutes}min"
    if cfg.aggregate_method.lower() == "mean":
        agg = valid["um"].resample(rule).mean()
    else:
        agg = valid["um"].resample(rule).median()

    proc = agg.dropna().to_frame("um")
    if proc.empty:
        return pd.DataFrame(), stats

    # Excluir por completo los intervalos que cruzan un mantenimiento.
    # Evita mezclar una instalación anterior y otra posterior dentro de una mediana.
    exclusions = parse_excluded_ranges(cfg.excluded_ranges_utc)
    for item in exclusions:
        end = item.end if item.end is not None else pd.Timestamp.now(tz="UTC")
        overlap = (proc.index <= end) & (proc.index + pd.Timedelta(minutes=minutes) > item.start)
        proc = proc.loc[~overlap]
    if proc.empty:
        return pd.DataFrame(), stats
    maintenance_breaks = pd.Series(False, index=proc.index)
    previous = pd.Series(proc.index, index=proc.index).shift()
    for item in exclusions:
        maintenance_breaks |= ((previous < item.start) & (proc.index >= item.start)).fillna(False)

    # 2) Sesiones temporales. Un hueco largo inicia una serie independiente.
    base_sessions = _assign_sessions(proc.index, cfg.session_gap_minutes)
    proc["session_id"] = base_sessions + maintenance_breaks.astype(int).cumsum()

    # 3) Salto anómalo SOLO dentro de una sesión continua. En vez de borrar el
    # punto (lo que podría crear otro salto artificial), el salto abre una NUEVA
    # sesión. Así conservamos el dato pero no lo interpretamos como contracción
    # o crecimiento continuo del tronco.
    in_session_diff = proc.groupby("session_id")["um"].diff().abs()
    stats.max_detected_jump_um = (
        float(in_session_diff.max()) if in_session_diff.notna().any() else None
    )

    jump_breaks = (
        (in_session_diff > cfg.max_jump_um).fillna(False)
        if cfg.max_jump_um > 0
        else pd.Series(False, index=proc.index)
    )
    if jump_breaks.any():
        last_jump_idx = jump_breaks[jump_breaks].index[-1]
        stats.last_jump_timestamp = pd.Timestamp(last_jump_idx)
        stats.last_jump_um = float(in_session_diff.loc[last_jump_idx])

    if cfg.max_jump_um > 0:
        # También preservamos los cortes creados por huecos de tiempo.
        time_breaks = pd.Series(proc.index, index=proc.index).diff() > pd.Timedelta(
            minutes=max(1, int(cfg.session_gap_minutes))
        )
        combined_breaks = (time_breaks.fillna(False) | jump_breaks | maintenance_breaks).astype(int)
        proc["session_id"] = combined_breaks.cumsum() + 1

    # 4) Suavizado y métricas siempre por sesión; nunca cruzan un hueco temporal.
    proc["smooth_um"] = _smooth_by_session(proc, cfg.rolling_window)
    proc["aggregate_relative_um"] = _relative_by_session(proc, "um")
    proc["relative_um"] = _relative_by_session(proc, "smooth_um")

    proc["growth_envelope_um"] = proc.groupby("session_id")["relative_um"].cummax()
    proc["water_deficit_um"] = proc["relative_um"] - proc["growth_envelope_um"]
    proc["trend_um"] = _trend_column(proc, cfg)

    stats.session_count = int(proc["session_id"].nunique())
    stats.valid_analysis_points = int(len(proc))

    # Métricas únicamente de la ÚLTIMA sesión operativa.
    latest_session_id = int(proc["session_id"].iloc[-1])
    current = proc.loc[proc["session_id"] == latest_session_id].copy()

    stats.latest_um = float(current["smooth_um"].iloc[-1])
    stats.last_valid_timestamp = pd.Timestamp(current.index[-1])

    # Con un solo punto no existe cambio real calculable.
    if len(current) >= 2:
        stats.delta_um = float(current["relative_um"].iloc[-1])
        stats.water_deficit_um = float(current["water_deficit_um"].iloc[-1])

    # Amplitud diaria: requiere cobertura real suficiente en el último día.
    local_dates = current.index.tz_convert(cfg.timezone_name).date
    last_day = local_dates[-1]
    day_values = current.loc[local_dates == last_day, "relative_um"]
    if len(day_values) >= 2:
        coverage_h = (
            day_values.index[-1] - day_values.index[0]
        ).total_seconds() / 3600.0
        if coverage_h >= float(cfg.daily_min_coverage_hours):
            stats.daily_amplitude_um = float(day_values.max() - day_values.min())

    # Recuperación vs máximo previo de 24 h: solo si la sesión tiene cobertura
    # temporal suficiente para que la comparación tenga sentido.
    session_span_h = (current.index[-1] - current.index[0]).total_seconds() / 3600.0
    if session_span_h >= float(cfg.daily_min_coverage_hours):
        last_ts = current.index[-1]
        previous_24h = current.loc[
            (current.index >= last_ts - pd.Timedelta(hours=24))
            & (current.index < last_ts),
            "relative_um",
        ]
        if len(previous_24h) >= 2:
            stats.recovery_gap_um = float(current["relative_um"].iloc[-1]) - float(
                previous_24h.max()
            )

    # Tendencia lenta: solo dentro de la última sesión y con cobertura mínima.
    stats.trend_rate_um_day = _trend_rate(
        current["trend_um"], cfg.trend_window_hours, cfg.trend_min_coverage_hours
    )

    _evaluate_alerts(stats, annotated, cfg)
    return proc, stats


def _evaluate_alerts(
    stats: SeriesStats, annotated_raw: pd.DataFrame, cfg: AppConfig
) -> None:
    if cfg.sensor_in_maintenance:
        stats.alert_level = "MANTENIMIENTO"
        stats.alert_message = (
            "DC1 en mantenimiento/pruebas. Los datos crudos se conservan, pero los rangos "
            "marcados se excluyen del análisis dendrométrico y las alarmas están pausadas."
        )
        return

    if stats.last_valid_timestamp is None:
        stats.alert_level = "SIN DATOS VÁLIDOS"
        stats.alert_message = (
            "No hay datos operativos válidos dentro de la ventana seleccionada."
        )
        return

    # Ceros consecutivos: solo datos NO excluidos del análisis.
    if not annotated_raw.empty:
        operational = annotated_raw.loc[~annotated_raw["analysis_excluded"]]
        raw = pd.to_numeric(operational.get("raw"), errors="coerce").dropna()
    else:
        raw = pd.Series(dtype=float)

    if cfg.consecutive_zero_alarm > 0 and len(raw):
        tail = raw.tail(cfg.consecutive_zero_alarm)
        if len(tail) == cfg.consecutive_zero_alarm and (tail.abs() < 1e-12).all():
            stats.alert_level = "REVISAR SENSOR"
            stats.alert_message = (
                f"Los últimos {cfg.consecutive_zero_alarm} valores operativos son 0. "
                "Revise alimentación, cableado, ADC e INA333."
            )
            return

    # Solo alertamos por un salto si ocurrió cerca del final de la serie válida.
    # Un salto histórico de semanas atrás no debe bloquear el estado actual.
    recent_jump = False
    if stats.last_jump_timestamp is not None and stats.last_valid_timestamp is not None:
        age = stats.last_valid_timestamp - stats.last_jump_timestamp
        recent_jump = age <= pd.Timedelta(minutes=max(60, cfg.aggregate_minutes * 2))

    if (
        cfg.max_jump_um > 0
        and recent_jump
        and stats.last_jump_um is not None
        and stats.last_jump_um > cfg.max_jump_um
    ):
        stats.alert_level = "SALTO ANÓMALO"
        stats.alert_message = (
            f"Se detectó un salto reciente entre intervalos de {stats.last_jump_um:.1f} µm; "
            f"el límite es {cfg.max_jump_um:.1f} µm. Se inició una nueva sesión de análisis."
        )
        return

    if cfg.sensor_reset_warning_um > 0 and stats.latest_um is not None and stats.latest_um >= cfg.sensor_reset_warning_um:
        stats.alert_level = "REAJUSTAR DC1"
        stats.alert_message = (
            f"Lectura operativa {stats.latest_um:.1f} µm. Se alcanzó el aviso de reajuste "
            f"configurado en {cfg.sensor_reset_warning_um:.0f} µm."
        )
        return

    if (
        cfg.water_deficit_alarm_um < 0
        and stats.water_deficit_um is not None
        and stats.water_deficit_um <= cfg.water_deficit_alarm_um
    ):
        stats.alert_level = "ALERTA DÉFICIT"
        stats.alert_message = (
            f"Déficit respecto del máximo previo de la sesión: {stats.water_deficit_um:.1f} µm; "
            f"umbral: {cfg.water_deficit_alarm_um:.1f} µm."
        )
        return

    if (
        cfg.daily_contraction_alarm_um > 0
        and stats.daily_amplitude_um is not None
        and stats.daily_amplitude_um >= cfg.daily_contraction_alarm_um
    ):
        stats.alert_level = "CONTRACCIÓN ALTA"
        stats.alert_message = (
            f"Amplitud diaria {stats.daily_amplitude_um:.1f} µm; "
            f"umbral {cfg.daily_contraction_alarm_um:.1f} µm."
        )
        return

    if (
        cfg.recovery_gap_alarm_um > 0
        and stats.recovery_gap_um is not None
        and stats.recovery_gap_um <= -cfg.recovery_gap_alarm_um
    ):
        stats.alert_level = "RECUPERACIÓN INCOMPLETA"
        stats.alert_message = (
            f"La señal está {abs(stats.recovery_gap_um):.1f} µm bajo el máximo previo; "
            f"umbral {cfg.recovery_gap_alarm_um:.1f} µm."
        )
        return

    if (
        cfg.negative_trend_alarm_um_day > 0
        and stats.trend_rate_um_day is not None
        and stats.trend_rate_um_day <= -cfg.negative_trend_alarm_um_day
    ):
        stats.alert_level = "TENDENCIA NEGATIVA"
        stats.alert_message = (
            f"Tendencia {stats.trend_rate_um_day:.1f} µm/día; límite negativo "
            f"{cfg.negative_trend_alarm_um_day:.1f} µm/día."
        )
        return

    if (
        cfg.warn_low_um < 0
        and stats.delta_um is not None
        and stats.delta_um <= cfg.warn_low_um
    ):
        stats.alert_level = "BAJO"
        stats.alert_message = f"Cambio relativo bajo: {stats.delta_um:.1f} µm."
        return

    if (
        cfg.warn_high_um > 0
        and stats.delta_um is not None
        and stats.delta_um >= cfg.warn_high_um
    ):
        stats.alert_level = "ALTO"
        stats.alert_message = f"Cambio relativo alto: {stats.delta_um:.1f} µm."
        return

    stats.alert_level = "NORMAL"
    stats.alert_message = "Señal dentro de los umbrales configurados."
