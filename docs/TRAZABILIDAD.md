# Trazabilidad SDD

## Línea base

| Spec | Área | Código principal | Estado | Evidencia actual |
|---|---|---|---|---|
| 001 | Plataforma y usuarios | `core/`, `homeApp/`, `UsuarioApp/`, `theme/`, templates compartidos | Baseline documentada | Inspección estática; sin pruebas funcionales recibidas |
| 002 | Proyectos | `ProyectosApp/`, templates de proyectos | Baseline documentada | Inspección estática; sin pruebas funcionales recibidas |
| 003 | Espacios | `EspaciosApp/`, templates de espacios | Baseline documentada | Inspección estática; sin pruebas funcionales recibidas |
| 004 | Dendrómetros | `DendometroApp/`, estáticos/templates, docs especializadas | Baseline documentada | 26 tests identificados; ejecución nueva bloqueada por entorno |

## Regla para cambios

Cada tarea implementada debe enlazar RF, archivos, migración si existe, pruebas/comprobaciones y resultado. `validation.md` registra evidencia del cambio; `docs/ESTADO_PROYECTO.md` conserva el punto de reanudación.
