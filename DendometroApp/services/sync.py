"""Carga reanudable por peticiones cortas. Sin hilos ni trabajos en memoria del worker."""
import uuid
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from ..models import Dendrometro, Lectura, Sincronizacion
from .thingspeak import fetch, ThingSpeakError


def status(job):
    duration = max(1, (job.fin - job.inicio).total_seconds())
    percent = 100 if job.estado == 'completa' else min(99, round(job.segundos_completos / duration * 100))
    return {'id': str(job.pk), 'estado': job.estado, 'progreso': percent,
            'registros': job.registros, 'omitidos': job.omitidos, 'error': job.error,
            'pendientes': len(job.rangos)}


def start(sensor, force=False):
    if not sensor.activo:
        raise ThingSpeakError('Este dendrómetro está deshabilitado para sincronizar.')
    active = sensor.sincronizaciones.filter(estado='pendiente').first()
    if active:
        return active
    now = timezone.now().replace(microsecond=0)
    if not force and sensor.ultima_sincronizacion and (now - sensor.ultima_sincronizacion).total_seconds() < sensor.config().refresh_seconds:
        return sensor.sincronizaciones.filter(estado='completa').order_by('-fin').first()
    cfg = sensor.config()
    cutoff = now - timedelta(hours=max(cfg.history_days * 24, cfg.realtime_hours))
    begin = cutoff
    if not force and sensor.sincronizado_desde and sensor.sincronizado_desde <= cutoff and sensor.ultima_sincronizacion:
        begin = max(cutoff, sensor.ultima_sincronizacion - timedelta(minutes=2))
    ranges = []
    end = now
    while end > begin:
        start_at = max(begin, end - timedelta(days=1))
        ranges.append([start_at.isoformat(), end.isoformat()])
        end = start_at
    try:
        with transaction.atomic():
            return Sincronizacion.objects.create(dendrometro=sensor, revision=sensor.revision,
                                                 inicio=begin, fin=now, rangos=ranges)
    except IntegrityError:
        return sensor.sincronizaciones.get(estado='pendiente')


def step(job):
    now, token = timezone.now(), uuid.uuid4()
    acquired = Sincronizacion.objects.filter(pk=job.pk, estado='pendiente').filter(
        Q(lease_until__isnull=True) | Q(lease_until__lt=now)
    ).update(lease_until=now + timedelta(seconds=90), lease_token=token)
    job.refresh_from_db()
    if not acquired:
        return job
    sensor = Dendrometro.objects.get(pk=job.dendrometro_id)
    try:
        if sensor.revision != job.revision or not sensor.activo:
            raise ThingSpeakError('La configuración cambió. Inicia una nueva sincronización.')
        begin, end = [parse_datetime(value) for value in job.rangos[0]]
        rows, count, skipped = fetch(sensor, begin, end)
        with transaction.atomic():
            # CAS: impide que un worker con lease vencido confirme datos sobre otro trabajo.
            current = Sincronizacion.objects.filter(pk=job.pk, estado='pendiente', lease_token=token)
            if not current.update(actualizado=timezone.now()):
                job.refresh_from_db()
                return job
            if Dendrometro.objects.get(pk=sensor.pk).revision != job.revision:
                raise ThingSpeakError('La configuración cambió. Inicia una nueva sincronización.')
            remaining = job.rangos[1:]
            if count >= 8000:
                if (end - begin).total_seconds() <= 2:
                    raise ThingSpeakError('Demasiadas entradas en el mismo segundo; no se puede asegurar una descarga completa.')
                middle = (begin + (end - begin) / 2).replace(microsecond=0)
                job.rangos = [[middle.isoformat(), end.isoformat()], [begin.isoformat(), middle.isoformat()]] + remaining
            else:
                Lectura.objects.bulk_create([Lectura(dendrometro=sensor, **row) for row in rows],
                                             update_conflicts=True, update_fields=['value', 'estado', 'entry_id'],
                                             unique_fields=['dendrometro', 'created_at'], batch_size=400)
                job.registros += len(rows)
                job.omitidos += skipped
                job.segundos_completos += (end - begin).total_seconds()
                job.rangos = remaining
            if not job.rangos:
                job.estado = 'completa'
                earliest = min(sensor.sincronizado_desde, job.inicio) if sensor.sincronizado_desde else job.inicio
                Dendrometro.objects.filter(pk=sensor.pk).update(ultima_sincronizacion=job.fin,
                                                               sincronizado_desde=earliest, ultimo_error='')
            job.lease_until = None
            job.lease_token = None
            job.actualizado = timezone.now()
            job.save()
    except ThingSpeakError as exc:
        Sincronizacion.objects.filter(pk=job.pk, lease_token=token).update(
            estado='error', error=str(exc), lease_until=None, lease_token=None, actualizado=timezone.now())
        Dendrometro.objects.filter(pk=sensor.pk).update(ultimo_error=str(exc))
        job.refresh_from_db()
    return job
