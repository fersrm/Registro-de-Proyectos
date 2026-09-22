# Plan técnico retrospectivo — Spec 004

- **Estado:** Arquitectura implementada; no es una propuesta de reconstrucción.

## Diseño existente

Modelos separados para sensor, lecturas y trabajos. Servicios independientes interpretan configuración, consultan ThingSpeak, procesan series, coordinan sincronización y construyen análisis/payloads. Vistas entregan páginas, JSON, pasos del trabajo y CSV. JS local usa Chart.js/Alpine empaquetados.

## Invariantes a preservar

- Clave solo en servidor.
- Lecturas crudas inmutables respecto del análisis.
- Unicidad/idempotencia e aislamiento por sensor.
- Revisiones de configuración y lease de trabajos.
- Zona horaria/unidades explícitas.
- Fallo remoto sin pérdida de datos válidos.

## Estrategia de pruebas existente

`DendometroApp/tests/settings.py` usa SQLite en memoria y desactiva middleware no pertinente. `test_module.py` contiene 26 casos de conversión, sesiones, métricas, permisos, secreto, CSRF, configuración, mantenimiento, señal obsoleta, idempotencia, saturación, fallos, concurrencia, importación y parsing remoto.

## Validación futura de cambios

Ejecutar suite completa más regresiones nuevas; `check` y migraciones secas; navegador para gráficos/progreso; exportaciones con contenido/límites; dobles de red por defecto. Una prueba real contra ThingSpeak debe ser separada, autorizada y sin registrar la clave.

## Riesgos

Cualquier ajuste a calibración, sesiones, agregación o filtros puede cambiar resultados históricos. Debe acompañarse de ejemplos numéricos, compatibilidad de configuración y decisión sobre recálculo.
