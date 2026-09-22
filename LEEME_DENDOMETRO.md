# DendometroApp — empieza aquí

Se incorporó el módulo de dendrómetros a tu plataforma Django.

1. Lee `docs/DENDOMETRO_INSTALACION.md` para integrar los archivos en tu copia actual.
2. Conserva tu `.env` y tu base de datos actual; no los reemplaces con los del ZIP.
3. En tu entorno virtual:

```bash
python -m pip install -r requirements_dendrometro.txt
python manage.py migrate
python manage.py check
```

En producción, ejecuta `python manage.py collectstatic --noinput` y recarga la web.

Entra en **Dendrómetros → Configuración**, registra el primer sensor y abre su visualización.

- Guía de uso, métricas y diferencias: `docs/DENDOMETRO_FUNCIONAMIENTO.md`.
- Pruebas y límites de verificación: `docs/DENDOMETRO_VALIDACION.md`.
- Capturas ilustrativas con datos sintéticos: `docs/dendometro_capturas/`.
- Importación de tu JSON y SQLite anterior: instrucciones en la guía de instalación.

Cada dendrómetro tiene configuración e historial independientes. La tarjeta de cambio mantiene la diferencia entre los dos últimos intervalos consecutivos (30 min por defecto).
