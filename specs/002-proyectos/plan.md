# Plan técnico retrospectivo — Spec 002

- **Estado:** Describe la arquitectura recibida; las correcciones son propuestas no autorizadas.

## Implementación existente

`Proyecto`, `IntegranteProyecto` y `RecursoProyecto` usan relaciones ORM y formsets inline. Las vistas genéricas gestionan lista, detalle, alta, edición y eliminación; `qrcode` genera PNG en memoria. Medios se guardan en rutas UUID por proyecto.

## Compatibilidad y datos

Futuras modificaciones deben preservar URLs/QR y archivos ya referenciados. Un cambio de permisos públicos necesita decisión y comunicación. Las correcciones de atomicidad pueden hacerse sin cambiar esquema; cualquier cambio de campo requiere migración versionada y reversión.

## Pruebas futuras

- Validaciones de fecha, longitudes, archivo/URL, formato y tamaño.
- Operación atómica con formset de integrantes o recursos inválido.
- Matriz de permisos incluyendo superusuario y sin perfil.
- Búsqueda, autoría, reemplazo de imagen, eliminación y QR público.
- Regresión de `RecursoProyecto.__str__`.

## Riesgos conocidos

Ver O-001 a O-004. No corregirlos dentro de otra tarea sin actualizar esta spec y autorizar tareas concretas.
