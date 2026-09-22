# Spec 002 — Proyectos

- **Estado:** Baseline documentada
- **Fecha de reconstrucción:** 2026-09-20

## Objetivo observado

Registrar y publicar proyectos agroeducativos con datos generales, nivel TRL, docente líder, integrantes, recursos e imágenes; permitir búsqueda, edición controlada, eliminación administrativa y acceso mediante QR.

## Acceso actual

| Acción | Anónimo | RESTRICTED | MANAGER/ADMIN | Superusuario |
|---|---:|---:|---:|---:|
| Lista/búsqueda | No | Sí | Sí | Sí |
| Detalle/QR | Sí | Sí | Sí | Sí |
| Crear | No | Sí | Sí | Sí |
| Editar | No | Solo si `creado_por` | Sí por cargo | Comportamiento a revisar si no tiene perfil |
| Eliminar | No | No | Sí | Sí |

## Requisitos reconstruidos

- **RF-002-01:** un proyecto registra título, fecha de inicio, organización, lugar, descripción, objetivos, TRL 1–8, docente líder y auditoría básica de creación/modificación.
- **RF-002-02:** admite hasta tres imágenes opcionales y múltiples integrantes con rol docente, estudiante o externo.
- **RF-002-03:** admite recursos con título, descripción y al menos archivo o URL.
- **RF-002-04:** fecha de inicio no puede ser futura; descripción mide 100–1200 caracteres y objetivos 50–300.
- **RF-002-05:** imágenes aceptan JPG/JPEG/PNG/WEBP hasta 5 MB; recursos aceptan formatos configurados hasta 30 MB.
- **RF-002-06:** la lista ordena por creación descendente y busca por título, organización o docente.
- **RF-002-07:** el detalle y el PNG QR son públicos según las vistas actuales; el QR apunta a la URL absoluta de detalle.
- **RF-002-08:** al editar se registra `modificado_por`; al reemplazar imágenes se gestionan archivos antiguos según el helper existente.
- **RF-002-09:** guardar proyecto, integrantes y recursos debe ser consistente como una sola operación lógica.
- **RF-002-10:** eliminar está restringido a ADMIN/MANAGER/superusuario.

## Casos límite

- Formsets secundarios inválidos después de que el objeto principal fue guardado.
- Usuario sin perfil o superusuario en edición/templates.
- Recurso sin archivo ni URL; archivo demasiado grande o extensión no permitida.
- Página pública accedida mediante ID enumerado.

## Criterios de aceptación de la conducta deseada

- **CA-002-01:** una creación válida persiste proyecto, integrantes y recursos con autor.
- **CA-002-02:** si cualquier parte es inválida, no queda un proyecto nuevo ni cambios parciales.
- **CA-002-03:** RESTRICTED no edita un proyecto ajeno ni elimina proyectos por URL directa.
- **CA-002-04:** un recurso inválido muestra errores sin perder datos del formulario.
- **CA-002-05:** el QR resuelve al detalle correcto; la condición pública se conserva solo mientras siga siendo decisión vigente.

## Observaciones relacionadas

O-001, O-002, O-003, O-004, O-006 y O-010.
