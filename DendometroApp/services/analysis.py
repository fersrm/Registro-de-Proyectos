from dataclasses import asdict
from datetime import timedelta
import json

import numpy as np
import pandas as pd
from django.utils import timezone

from .processing import annotate_raw_series, process_series, parse_excluded_ranges, input_to_um


def load(sensor):
    cfg = sensor.config()
    cutoff = timezone.now() - timedelta(hours=max(cfg.history_days * 24, cfg.realtime_hours))
    raw = pd.DataFrame.from_records(sensor.lecturas.filter(created_at__gte=cutoff).values('created_at', 'entry_id', 'value', 'estado'),
                                    columns=['created_at', 'entry_id', 'value', 'estado'])
    raw['created_at'] = pd.to_datetime(raw['created_at'], utc=True)
    analysis_raw = raw.loc[raw.created_at >= pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=cfg.history_days)]
    proc, stats = process_series(analysis_raw, cfg)
    annotated = annotate_raw_series(raw, cfg)
    latest = sensor.lecturas.order_by('-created_at').first()
    if latest:
        stats.latest_signal_um = float(input_to_um(pd.Series([latest.value]), cfg).iloc[0])
        stats.latest_signal_timestamp = pd.Timestamp(latest.created_at)
    age = (timezone.now() - latest.created_at).total_seconds() / 60 if latest else None
    if cfg.sensor_in_maintenance:
        stats.alert_level = 'MANTENIMIENTO'
        stats.alert_message = 'Alarmas pausadas y métricas actuales ocultas. Las lecturas crudas se conservan.'
    elif age is None or age > cfg.stale_minutes:
        stats.alert_level = 'SIN DATOS' if age is None else 'DATOS ATRASADOS'
        stats.alert_message = 'Todavía no se han recibido lecturas.' if age is None else f'Última lectura hace {age:.0f} minutos. Comprueba el sensor y la conexión.'
    elif cfg.consecutive_zero_alarm > 0 and not raw.empty:
        # Los ceros se diagnostican aun si se excluyeron de las métricas fisiológicas.
        operational = raw.copy()
        for item in parse_excluded_ranges(cfg.excluded_ranges_utc):
            end = item.end if item.end is not None else pd.Timestamp.now(tz='UTC')
            operational = operational.loc[~((operational.created_at >= item.start) & (operational.created_at <= end))]
        tail = operational.value.tail(cfg.consecutive_zero_alarm)
        if len(tail) == cfg.consecutive_zero_alarm and (tail.abs() < 1e-12).all():
            stats.alert_level = 'REVISAR SENSOR'
            stats.alert_message = f'Últimas {len(tail)} lecturas operativas en cero. Revisa alimentación, cableado y ADC.'
    return raw, annotated, proc, stats, latest


def interval_delta(proc, minutes):
    if proc.empty:
        return None
    current = proc.loc[proc.session_id == proc.session_id.iloc[-1], 'um'].dropna()
    if len(current) < 2 or current.index[-1] - current.index[-2] != pd.Timedelta(minutes=minutes):
        return None
    return float(current.iloc[-1] - current.iloc[-2])


def records(frame, limit=6000):
    """Reducción visual únicamente; las métricas y CSV usan todos los datos."""
    reduced = len(frame) > limit
    if reduced:
        indices = np.unique(np.linspace(0, len(frame) - 1, limit).astype(int))
        frame = frame.iloc[indices]
    return json.loads(frame.to_json(orient='records', date_format='iso')), reduced


def payload(sensor, selected=None):
    raw, annotated, proc, stats, latest = load(sensor)
    cfg = sensor.config()
    metrics = asdict(stats)
    metrics['interval_delta_um'] = interval_delta(proc, cfg.aggregate_minutes)
    metrics['session_change_um'] = metrics['delta_um']
    if cfg.sensor_in_maintenance:
        for key in ['delta_um', 'interval_delta_um', 'session_change_um', 'daily_amplitude_um', 'water_deficit_um', 'recovery_gap_um', 'trend_rate_um_day']:
            metrics[key] = None
    sessions, historic, detail = [], [], []
    reduced_history = reduced_detail = False
    chosen = None
    if not proc.empty:
        for sid, group in proc.groupby('session_id'):
            sessions.append({'id': int(sid), 'inicio': group.index[0].isoformat(), 'fin': group.index[-1].isoformat(), 'puntos': len(group)})
            # Separar las series antes de reducir: ningún trazo cruza sesiones.
            values, reduced = records(group.reset_index()[['created_at', 'um']], limit=max(2, 6000 // max(1, stats.session_count)))
            historic.append({'id': int(sid), 'points': values})
            reduced_history |= reduced
        chosen = sessions[-1]['id']
        ids = [s['id'] for s in sessions]
        if selected in ids:
            chosen = selected
        elif sessions[-1]['puntos'] < 2:
            usable = [s['id'] for s in sessions if s['puntos'] >= 2]
            if usable:
                chosen = usable[-1]
        detail, reduced_detail = records(proc.loc[proc.session_id == chosen].reset_index())
    realtime = annotated
    if not realtime.empty:
        realtime = realtime.loc[realtime.created_at >= pd.Timestamp.now(tz='UTC') - pd.Timedelta(hours=cfg.realtime_hours)]
    realtime_points, reduced_rt = records(realtime)
    minute_points = []
    if not realtime.empty:
        minute = realtime.set_index('created_at')['um'].resample('1min').median().reset_index()
        minute_points, reduced_minute = records(minute)
        reduced_rt |= reduced_minute
    current_interval_partial = False
    if not proc.empty:
        current_interval_partial = proc.index[-1] + pd.Timedelta(minutes=cfg.aggregate_minutes) > pd.Timestamp.now(tz='UTC')
    for key, value in metrics.items():
        if isinstance(value, pd.Timestamp):
            metrics[key] = value.isoformat()
        elif isinstance(value, float) and not np.isfinite(value):
            metrics[key] = None
    logical = '—'
    if latest and latest.estado is not None:
        logical = {0: 'INACTIVO', 1: 'ACTIVO'}.get(latest.estado, str(latest.estado))
    return {'sensor': {'id': sensor.pk, 'nombre': sensor.nombre, 'ubicacion': sensor.ubicacion,
                       'canal': sensor.channel_id, 'activo': sensor.activo, 'intervalo': cfg.aggregate_minutes,
                       'refresh_seconds': cfg.refresh_seconds, 'timezone': cfg.timezone_name,
                       'maintenance': cfg.sensor_in_maintenance, 'show_envelope': cfg.show_growth_envelope,
                       'show_trend': cfg.show_slow_trend, 'warn_low_um': cfg.warn_low_um, 'warn_high_um': cfg.warn_high_um, 'ultima_sincronizacion': sensor.ultima_sincronizacion.isoformat() if sensor.ultima_sincronizacion else None,
                       'ultimo_error': sensor.ultimo_error},
            'metrics': metrics, 'logical_state': logical,
            'last_received': latest.created_at.isoformat() if latest else None,
            'raw_count': len(raw), 'sessions': sessions, 'selected_session': chosen,
            'latest_session': sessions[-1]['id'] if sessions else None,
            'historic': historic, 'detail': detail, 'realtime': realtime_points, 'minute_median': minute_points,
            'reduced': reduced_history or reduced_detail or reduced_rt,
            'partial_interval': current_interval_partial}
