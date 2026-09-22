# Trazabilidad SDD

## Línea base

| Spec | Área | Código principal | Estado | Evidencia actual |
|---|---|---|---|---|
| 001 | Plataforma y usuarios | `core/`, `homeApp/`, `UsuarioApp/`, `theme/`, templates compartidos | Baseline documentada | Inspección estática; sin pruebas funcionales recibidas |
| 002 | Proyectos | `ProyectosApp/`, templates de proyectos | Baseline documentada | Inspección estática; sin pruebas funcionales recibidas |
| 003 | Espacios | `EspaciosApp/`, templates de espacios | Baseline documentada | Inspección estática; sin pruebas funcionales recibidas |
| 004 | Dendrómetros | `DendometroApp/`, estáticos/templates, docs especializadas | Baseline documentada | 26 tests identificados; ejecución nueva bloqueada por entorno |

## Cambios propuestos

| Spec | Área | Requisitos | Código previsto | Estado | Evidencia prevista |
|---|---|---|---|---|---|
| 005 | Observaciones O-001 a O-010, auditoría y cierre de sesión | RF-005-01 a RF-005-15 y ajuste posterior | `ProyectosApp/`, `UsuarioApp/`, `homeApp/`, `EspaciosApp/`, `core/mixins.py`, templates, `theme/static_src/tailwind.config.js`, `.gitignore`, migraciones locales | Implementada y validada; aceptación pendiente | 53 tests, checks, migraciones secas, build Tailwind offline e inspección visual escritorio/móvil; cierre directo por POST/CSRF sin pruebas adicionales por instrucción del propietario |

## Regla para cambios

Cada tarea implementada debe enlazar RF, archivos, migración si existe, pruebas/comprobaciones y resultado. `validation.md` registra evidencia del cambio; `docs/ESTADO_PROYECTO.md` conserva el punto de reanudación.

Para la spec 005, el mapeo detallado RF → archivos → evidencia está en `specs/005-correcciones-observaciones-y-auditoria/plan.md` y los resultados reales en `validation.md`.
