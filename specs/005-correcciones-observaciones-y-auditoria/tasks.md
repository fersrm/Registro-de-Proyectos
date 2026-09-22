# Tareas — Spec 005: correcciones de observaciones y auditoría

Spec: [spec.md](spec.md). Plan: [plan.md](plan.md).
Estado: implementación y validación completadas; aceptación del propietario pendiente.
Implementación autorizada: SÍ, por instrucción posterior del 2026-09-22.

- [x] **T-005-01 — Habilitar el versionado de migraciones locales y fijar la línea base.**
  - RF: RF-005-10.
  - Depende de: ninguna.
  - Archivos previstos: `.gitignore`, migraciones existentes de apps locales.
  - Hecho cuando: las migraciones `.py` dejan de estar ignoradas, caches continúan excluidas, la cadena histórica se incorpora sin modificar `db.sqlite3` y se documenta el estado aplicado.

- [x] **T-005-02 — Crear el modelo y la migración aditiva de auditoría de proyectos.**
  - RF: RF-005-12, RF-005-13, RF-005-14.
  - Depende de: T-005-01.
  - Archivos previstos: `ProyectosApp/models.py`, `ProyectosApp/migrations/<nueva>.py`; `ProyectosApp/admin.py` solo si se autoriza consulta técnica.
  - Hecho cuando: el esquema representa acción, fecha, proyecto/actor opcionales y snapshots mínimos, sin backfill ficticio ni migración destructiva.

- [x] **T-005-03 — Corregir atomicidad y emitir eventos de alta/modificación.**
  - RF: RF-005-03, RF-005-04, RF-005-12, RF-005-13.
  - Depende de: T-005-02.
  - Archivos previstos: `ProyectosApp/views.py`, posiblemente helpers locales de `ProyectosApp`.
  - Hecho cuando: formulario principal, integrantes, recursos y evento se guardan todos o ninguno; no hay doble guardado ni evento ante validación o rollback fallido.

- [x] **T-005-04 — Auditar la eliminación autorizada de proyectos.**
  - RF: RF-005-06, RF-005-13, RF-005-14.
  - Depende de: T-005-02.
  - Archivos previstos: `ProyectosApp/views.py`.
  - Hecho cuando: solo ADMIN/MANAGER/superusuario eliminan, el evento participa de la transacción y sobrevive con identidad mínima del proyecto y actor.

- [x] **T-005-05 — Corregir la representación textual de recursos.**
  - RF: RF-005-05.
  - Depende de: ninguna.
  - Archivos previstos: `ProyectosApp/models.py`.
  - Hecho cuando: `str(recurso)` usa campos existentes y funciona con archivo, URL o ambos.

- [x] **T-005-06 — Unificar permisos de vistas y templates.**
  - RF: RF-005-06, RF-005-11, RF-005-12.
  - Depende de: ninguna.
  - Archivos previstos: `core/mixins.py`, `ProyectosApp/views.py`, nuevo `UsuarioApp/templatetags/`, `templates/components/navbar/nav.html`, `templates/pages/index.html`, `templates/pages/UsuarioApp/usuarios_lista.html`, `templates/pages/proyectos/proyecto_list.html`, `templates/pages/proyectos/proyecto_detail.html` y otros usos directos encontrados al implementar.
  - Hecho cuando: servidor y UI coinciden para ADMIN, MANAGER, RESTRICTED, superusuario, sin perfil y anónimo, sin conceder permisos por ausencia de datos.

- [x] **T-005-07 — Retirar el gráfico de ejemplo del inicio.**
  - RF: RF-005-07.
  - Depende de: ninguna.
  - Archivos previstos: `templates/pages/index.html`.
  - Hecho cuando: el template no carga ECharts ni `grafico_home.js`, no se elimina contenido usado y la página renderiza sin solicitudes 404 asociadas.

- [x] **T-005-08 — Corregir las fuentes de contenido de Tailwind.**
  - RF: RF-005-09.
  - Depende de: T-005-06, T-005-07 para compilar el conjunto final de templates.
  - Archivos previstos: `theme/static_src/tailwind.config.js`, `theme/static/css/dist/styles.css` como artefacto generado solo si la política actual lo versiona.
  - Hecho cuando: globs específicos cubren `static/js/mensajes.js` y Python local con clases, excluyen dependencias/entornos, y `py manage.py tailwind build` finaliza correctamente.

- [x] **T-005-09 — Crear regresiones funcionales de proyectos.**
  - RF: RF-005-01, RF-005-03 a RF-005-06, RF-005-10, RF-005-12 a RF-005-14.
  - Depende de: T-005-02 a T-005-06.
  - Archivos previstos: reemplazo de `ProyectosApp/tests.py` por `ProyectosApp/tests/` o suite equivalente.
  - Hecho cuando: existen y pasan casos de atomicidad, archivos, permisos, detalle/QR público, `__str__` y auditoría, incluidos fallos y rollback.

- [x] **T-005-10 — Crear regresiones funcionales de usuarios e inicio.**
  - RF: RF-005-06, RF-005-07, RF-005-08, RF-005-11.
  - Depende de: T-005-06, T-005-07.
  - Archivos previstos: reemplazo de `UsuarioApp/tests.py` y `homeApp/tests.py` por suites reales.
  - Hecho cuando: se prueban login, listado para todo autenticado, acciones por cargo, signup cerrado, perfil ausente, superusuario, inicio y actividad, con métodos HTTP y accesos directos.

- [x] **T-005-11 — Crear regresiones funcionales de espacios.**
  - RF: RF-005-02, RF-005-08.
  - Depende de: ninguna.
  - Archivos previstos: reemplazo de `EspaciosApp/tests.py` por suite real.
  - Hecho cuando: lista autenticada, ficha/QR públicos, destino y 404 desconocido están cubiertos.

- [x] **T-005-12 — Ejecutar validación automatizada y visual.**
  - RF: RF-005-01 a RF-005-15.
  - Depende de: T-005-01 a T-005-11.
  - Archivos previstos: nuevo `specs/005-correcciones-observaciones-y-auditoria/validation.md`; sin datos reales ni secretos.
  - Hecho cuando: se registran resultados de tests/checks/migraciones secas/build, se ejecuta la suite aislada de dendrómetros y se inspeccionan en navegador las vistas afectadas en escritorio/móvil.

- [x] **T-005-13 — Actualizar documentación con evidencia real.**
  - RF: RF-005-01 a RF-005-15.
  - Depende de: T-005-12.
  - Archivos previstos: spec 005, `specs/README.md`, `docs/PROYECTO.md`, `docs/ESTADO_PROYECTO.md`, `docs/DECISIONES.md`, `docs/TRAZABILIDAD.md`, `docs/ARQUITECTURA.md`.
  - Hecho cuando: se distingue propuesta de implementación real, los comandos y límites constan en validación y no se marca aceptación del propietario automáticamente.

## Autorización posterior

Recibida el 2026-09-22 para implementar la spec completa. No autorizó producción, despliegue, datos reales, commit ni push.

## Ejecución

| Fecha | Tarea | Archivos / comando | Resultado / pendiente |
|---|---|---|---|
| 2026-09-22 | Documentación de T-005-01 a T-005-13 | Solo Markdown | Propuesta creada; ninguna tarea de código iniciada. |
| 2026-09-22 | T-005-01 a T-005-11 | Código, templates, configuración, migraciones y pruebas descritos en el plan | Implementados; detalle de archivos en `validation.md`. |
| 2026-09-22 | T-005-12 | 53 tests, 2 checks, 2 comprobaciones secas de migración, build Tailwind e inspección visual | Aprobado; el comando literal con `py` no estuvo disponible y se usó el runtime aislado equivalente. |
| 2026-09-22 | T-005-13 | Spec 005, índices y documentación del proyecto | Actualizados con evidencia real. |
| 2026-09-22 | T-005-14 | Navegación lateral y menú de perfil | Implementado: cierre directo mediante formularios POST con CSRF; no se ejecutaron pruebas por solicitud expresa del propietario. |

## Ajuste pequeño posterior

- [x] **T-005-14 — Cerrar sesión directamente desde la navegación.**
  - RF: ajuste posterior de cierre de sesión directo.
  - Archivos: `templates/components/navbar/nav.html`, `templates/components/header/components/profile.html`.
  - Hecho cuando: ambos controles envían `POST` al endpoint de logout con CSRF y no muestran la confirmación de allauth.

## Reanudación

Última acción real: implementación, pruebas automatizadas, build e inspección visual completados.

Siguiente paso: revisión y aceptación del propietario. No se aplicó la migración a la base local ni a producción.

Pendientes fuera de alcance: decidir si `/espacios/` debe ser público y si se necesita una interfaz de consulta de auditoría.

## Aceptación del usuario

Pendiente; no se presupone por la creación de estos documentos ni se marcará automáticamente después de ejecutar pruebas.
