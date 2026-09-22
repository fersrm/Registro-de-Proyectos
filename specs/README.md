# Catálogo de especificaciones

## Estados

- **Baseline documentada:** describe código existente; no ordena reconstruirlo ni certifica aceptación.
- **Propuesta:** documentos creados, pendientes de revisión.
- **Aprobada para implementar:** el usuario autorizó explícitamente alcance/tareas.
- **En implementación / Validación / Cerrada:** estados posteriores con evidencia.

## Specs actuales

| ID | Nombre | Estado | Descripción |
|---|---|---|---|
| 001 | Plataforma y usuarios | Baseline documentada | Autenticación, cargos, perfiles, inicio, navegación y tema |
| 002 | Proyectos | Baseline documentada | Proyectos, integrantes, recursos, imágenes, permisos y QR |
| 003 | Espacios | Baseline documentada | Catálogo y ficha/QR de espacios |
| 004 | Dendrómetros | Baseline documentada | Configuración, sincronización, análisis, gráficos y exportación |
| 005 | Correcciones de observaciones y auditoría | Implementada y validada; aceptación pendiente | O-001 a O-010: atomicidad, permisos, pruebas, Tailwind, migraciones y auditoría de proyectos |

Siguiente número libre observado: **006**. Verificarlo siempre antes de crear una carpeta.

## Convención

Carpeta `NNN-nombre-corto/` con `spec.md`, `plan.md`, `tasks.md` y, tras implementar, `validation.md`. Los requisitos usan `RF-NNN-XX`; tareas `T-NNN-XX`. Un cambio pequeño se agrega a la spec vigente con fecha y conserva IDs históricos.

Copiar las plantillas desde `_templates/` conceptualmente; completar contenido real y eliminar instrucciones internas. No marcar requisitos aprobados ni tareas completas sin decisión/evidencia.
