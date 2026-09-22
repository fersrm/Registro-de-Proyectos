"""Solo lectura HTTPS; las claves y los errores del proveedor no llegan al navegador."""

import math
from datetime import timezone as dt_timezone

import requests
from django.utils.dateparse import parse_datetime


class ThingSpeakError(Exception):
    pass


def finite(value):
    try:
        result = float(value)
        return result if math.isfinite(result) else None
    except (TypeError, ValueError):
        return None


def fetch(sensor, start=None, end=None, results=8000):
    params = {"results": results, "timezone": "UTC"}
    if sensor.read_api_key:
        params["api_key"] = sensor.read_api_key
    for key, value in [("start", start), ("end", end)]:
        if value is not None:
            params[key] = value.astimezone(dt_timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    try:
        response = requests.get(
            f"https://api.thingspeak.com/channels/{sensor.channel_id}/feeds.json",
            params=params,
            timeout=(5, 20),
        )
        if response.status_code != 200:
            raise ThingSpeakError(
                f"ThingSpeak respondió HTTP {response.status_code}. Revisa el canal, la clave de lectura o intenta nuevamente."
            )
        payload = response.json()
    except (requests.RequestException, ValueError):
        raise ThingSpeakError(
            "No se pudo consultar ThingSpeak. Revisa la conexión y vuelve a intentar."
        ) from None
    if (
        not isinstance(payload, dict)
        or not isinstance(payload.get("feeds"), list)
        or not isinstance(payload.get("channel"), dict)
    ):
        raise ThingSpeakError(
            "ThingSpeak no entregó un canal válido. Revisa el Channel ID y la Read API Key."
        )
    field = f"field{sensor.field_id}"
    if not payload["channel"].get(field):
        raise ThingSpeakError("El campo de señal configurado no existe en el canal.")
    readings, skipped = [], 0
    for feed in payload["feeds"]:
        if not isinstance(feed, dict):
            skipped += 1
            continue
        value = finite(feed.get(field))
        try:
            timestamp = parse_datetime(str(feed.get("created_at", "")))
            if timestamp is None:
                raise ValueError()
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=dt_timezone.utc)
            entry = int(feed["entry_id"]) if feed.get("entry_id") is not None else None
        except (ValueError, TypeError, OverflowError):
            skipped += 1
            continue
        if value is None:
            skipped += 1
            continue
        if start and timestamp < start or end and timestamp > end:
            continue
        readings.append(
            {
                "created_at": timestamp,
                "entry_id": entry,
                "value": value,
                "estado": finite(feed.get(f"field{sensor.state_field_id}")),
            }
        )
    return readings, len(payload["feeds"]), skipped
