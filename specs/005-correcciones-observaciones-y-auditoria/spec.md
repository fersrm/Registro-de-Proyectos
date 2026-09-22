# Spec 005 — Correcciones de observaciones y auditoría de proyectos

- **Estado:** Implementada y validada; aceptación del propietario pendiente
- **Fecha:** 2026-09-22
- **Módulos afectados:** `ProyectosApp`, `UsuarioApp`, `homeApp`, `EspaciosApp`, `theme` y configuración del repositorio
- **Fuente:** solicitud del propietario sobre O-001 a O-010 de `docs/OBSERVACIONES_PROYECTO.md`
- **Implementación autorizada:** SÍ, por instrucción posterior del 2026-09-22
- **Revisión del usuario:** alcance documental revisado; aceptación final del resultado pendiente

## Problema y resultado esperado

La línea base registra defectos de atomicidad, representación textual, permisos inconsistentes, recursos estáticos obsoletos, falta de pruebas y una regla de Git que oculta migraciones. Además, el propietario confirmó políticas existentes de acceso público y creación de proyectos, y solicitó que las altas, modificaciones y eliminaciones de proyectos dejen auditoría persistente.

El resultado esperado es un cambio transversal y acotado que:

1. conserve como públicos el detalle y QR de proyectos y las fichas y QR de espacios;
2. haga atómico el guardado de proyecto, integrantes y recursos;
3. corrija la representación de recursos y unifique permisos de servidor e interfaz;
4. retire el gráfico de ejemplo no utilizado del inicio;
5. añada regresiones funcionales a las apps que hoy solo tienen esqueletos de prueba;
6. incluya las fuentes dinámicas reales en el escaneo de Tailwind y valide con el comando del proyecto;
7. permita versionar las migraciones de las apps locales; y
8. registre quién creó, modificó o eliminó cada proyecto, incluso después de su eliminación.

Aunque la solicitud menciona principalmente `DendometroApp`, ninguna observación O-001 a O-010 exige cambiar su lógica. Su comportamiento y su suite existente se preservan como regresión.

## Resolución de las observaciones

| Observación | Decisión de esta spec | Cambio funcional previsto |
|---|---|---|
| O-001 | Confirmada | Conservar públicos detalle/QR de proyecto y ficha/QR de espacio. Las listas conservan el acceso actual. |
| O-002 | Corregir | Validar formulario principal y ambos formsets antes de confirmar una única transacción. |
| O-003 | Corregir | `str(recurso)` no dependerá de un campo `tipo` inexistente. |
| O-004 | Corregir | Servidor y plantillas usarán una política segura común para cargo, superusuario y ausencia de perfil. |
| O-005 | Corregir | Retirar del inicio la carga del JS inexistente y de ECharts, que quedó como dependencia del ejemplo. |
| O-006 | Corregir | Añadir pruebas funcionales a `homeApp`, `UsuarioApp`, `ProyectosApp` y `EspaciosApp`. |
| O-007 | Corregir | Escanear las fuentes dinámicas reales de Tailwind y ejecutar `py manage.py tailwind build`. |
| O-008 | Corregir | Dejar de ignorar globalmente `migrations/` y versionar la cadena local existente y la nueva migración. |
| O-009 | Confirmada | El listado de usuarios sigue disponible para cualquier usuario autenticado; no se hace público para anónimos. |
| O-010 | Confirmada y ampliada | Cualquier usuario autenticado puede crear proyectos; las operaciones de crear, modificar y eliminar generan auditoría. |

## Actores y permisos

| Acción / datos | Anónimo | RESTRICTED autenticado | MANAGER/ADMIN | Superusuario | Autenticado sin perfil |
|---|---:|---:|---:|---:|---:|
| Ver lista de proyectos | No | Sí | Sí | Sí | Sí |
| Ver detalle/QR de proyecto | Sí | Sí | Sí | Sí | Sí |
| Crear proyecto | No | Sí | Sí | Sí | Sí |
| Editar proyecto propio | No | Sí | Sí | Sí | No |
| Editar proyecto ajeno | No | No | Sí | Sí | No |
| Eliminar proyecto | No | No | Sí | Sí | No |
| Ver lista de espacios | No | Sí | Sí | Sí | Sí |
| Ver ficha/QR de espacio | Sí | Sí | Sí | Sí | Sí |
| Ver lista de usuarios | No | Sí | Sí | Sí | Sí |
| Crear/activar/desactivar usuarios | No | No | Sí | Sí | No |
| Generar eventos de auditoría de proyecto | No aplica | Automático al operar | Automático al operar | Automático al operar | Automático al crear |
| Consultar auditoría mediante una UI nueva | No | No incluida | No incluida | No incluida | No incluida |

Las autorizaciones se aplican en servidor, incluso por URL directa y método HTTP. La interfaz puede ocultar controles no permitidos, pero no sustituye estas reglas. Un superusuario no necesita perfil ni cargo para acciones administrativas. Un usuario sin perfil no recibe permisos de cargo por omisión.

## Alcance

Incluye:

- corregir los defectos O-002 a O-008;
- formalizar las políticas confirmadas de O-001, O-009 y O-010;
- auditar altas, modificaciones y eliminaciones de `Proyecto`;
- considerar como modificación del proyecto un guardado exitoso que cambie el objeto principal, integrantes o recursos;
- conservar URLs públicas, QR, archivos existentes y datos históricos;
- cubrir permisos y casos negativos con pruebas automatizadas;
- actualizar documentación y evidencia de validación al implementar.

No incluye:

- hacer públicos los listados de proyectos, espacios o usuarios;
- exponer la auditoría en una página, API, exportación o QR;
- guardar un diff completo ni copias de archivos o descripciones en auditoría;
- auditar acciones de usuarios, espacios o dendrómetros;
- cambiar matemáticas, sincronización, permisos o datos de `DendometroApp`;
- activar correo real, `django-axes`, registro público o despliegues;

## Ajuste pequeño posterior — cierre de sesión directo

- **Fecha:** 2026-09-22
- **Autorización:** solicitud directa posterior del propietario.
- **Resultado esperado:** al pulsar "Cerrar sesión" desde la navegación lateral o el menú de perfil, la sesión finaliza y redirige al login sin mostrar la pantalla intermedia de confirmación.
- **Seguridad:** el cierre se mantiene como una solicitud `POST` protegida con CSRF; no se habilita `ACCOUNT_LOGOUT_ON_GET` ni se permite cerrar sesión por enlace `GET`.
- reconstruir módulos existentes o añadir dependencias.

## Historias y flujos

### Guardado atómico y auditoría

1. Un usuario autenticado envía el proyecto, integrantes y recursos.
2. El servidor valida las tres partes sin confirmar cambios parciales.
3. Si alguna parte es inválida, se muestran sus errores y no se persiste ni el proyecto ni un evento de auditoría.
4. Si todo es válido, se guardan las tres partes y un único evento `CREAR` o `MODIFICAR` dentro de la misma operación atómica.
5. El evento `MODIFICAR` también se genera si el cambio válido afecta solo integrantes o recursos.

### Eliminación auditada

1. Solo ADMIN, MANAGER o superusuario pueden solicitar la eliminación por el método admitido.
2. En la misma transacción se conserva un evento `ELIMINAR` con actor, fecha, ID original y título del proyecto.
3. Si la eliminación falla o se revierte, tampoco debe quedar un evento que declare una eliminación inexistente.
4. El evento sobrevive al borrado del proyecto y a la eliminación posterior de la cuenta del actor mediante valores de referencia histórica.

## Requisitos funcionales

- **RF-005-01:** CUANDO una persona anónima solicita el detalle o QR de un proyecto existente, EL SISTEMA lo entrega sin exigir cuenta ni login; un ID inexistente responde 404.
- **RF-005-02:** CUANDO una persona anónima solicita una ficha o QR de espacio existente, EL SISTEMA lo entrega sin exigir cuenta ni login; la lista de espacios conserva autenticación y un ID de QR desconocido responde 404.
- **RF-005-03:** CUANDO se crea o edita un proyecto, EL SISTEMA valida el formulario principal, integrantes y recursos antes de confirmar, y persiste todo o nada dentro de una transacción.
- **RF-005-04:** SI un integrante o recurso es inválido, ENTONCES no queda un proyecto nuevo, ningún cambio parcial ni un evento de auditoría de éxito.
- **RF-005-05:** CUANDO un `RecursoProyecto` se convierte a texto, EL SISTEMA devuelve una representación estable basada en campos existentes y nunca intenta acceder a `tipo`.
- **RF-005-06:** CUANDO se decide si un usuario puede editar/eliminar o ver controles administrativos, EL SISTEMA aplica la misma política segura: ADMIN/MANAGER y superusuario reciben permisos administrativos; RESTRICTED solo edita proyectos propios; la falta de perfil no concede permisos ni provoca error.
- **RF-005-07:** CUANDO se renderiza el inicio, EL SISTEMA no solicita `grafico_home.js` ni la librería ECharts que solo lo respaldaba.
- **RF-005-08:** EL SISTEMA dispone de pruebas funcionales para inicio/actividad, usuarios/perfiles, proyectos/archivos/permisos/auditoría y espacios/QR, además de conservar la suite de dendrómetros.
- **RF-005-09:** CUANDO se compila Tailwind, EL ESCANEO incluye las clases declaradas en el JavaScript propio y Python que hoy generan clases, sin incluir dependencias ni `.venv`; la compilación oficial del cambio usa `py manage.py tailwind build`.
- **RF-005-10:** EL REPOSITORIO permite versionar migraciones de las apps locales, conserva su cadena histórica actual y excluye únicamente artefactos como `__pycache__` y bytecode.
- **RF-005-11:** CUANDO cualquier usuario autenticado solicita el listado de usuarios, EL SISTEMA permite la consulta; un anónimo continúa dirigido al login y solo cargos autorizados o superusuario ven y ejecutan acciones administrativas.
- **RF-005-12:** CUANDO cualquier usuario autenticado crea un proyecto válido, EL SISTEMA conserva `creado_por`/`modificado_por` y genera un evento de auditoría `CREAR` asociado al actor.
- **RF-005-13:** CUANDO una modificación válida se confirma o una eliminación autorizada se completa, EL SISTEMA genera exactamente un evento `MODIFICAR` o `ELIMINAR`, respectivamente, en la misma transacción.
- **RF-005-14:** SI un proyecto o la cuenta del actor deja de existir, ENTONCES los eventos históricos conservan como mínimo acción, fecha, ID original y título del proyecto, e identificador y nombre de usuario del actor disponibles al momento del evento.
- **RF-005-15:** EL CAMBIO no altera las lecturas crudas, análisis, configuración, secretos, sincronización ni permisos existentes de `DendometroApp`.

## Datos y reglas de auditoría

Se propone un modelo local de eventos de proyecto con los siguientes datos mínimos:

| Dato | Regla |
|---|---|
| Acción | Enumeración cerrada: `CREAR`, `MODIFICAR`, `ELIMINAR`. |
| Fecha/hora | Asignada por servidor, con zona horaria habilitada e inmutable. |
| Proyecto relacionado | Relación opcional al proyecto vivo, sin provocar el borrado del evento. |
| ID original y título | Copia mínima obligatoria para identificar un proyecto eliminado. |
| Actor relacionado | Relación opcional a `User`, con `SET_NULL`. |
| ID y username del actor | Copia mínima para conservar autoría si la cuenta se elimina. |

Los eventos no aceptan edición desde formularios de usuario y no guardan claves, archivos, imágenes, descripciones completas ni datos de ThingSpeak. No se crean eventos sintéticos para proyectos históricos: sus campos actuales `creado_por`, `modificado_por`, `creado` y `modificado` permanecen como antecedente. No se incorpora una purga automática en este cambio.

## Criterios de aceptación

| RF | Dado / cuando | Entonces |
|---|---|---|
| RF-005-01 | Anónimo abre detalle y QR de un proyecto válido | Recibe 200 y el QR apunta al detalle público; un PK ausente entrega 404. |
| RF-005-02 | Anónimo abre `espacio_1` y su QR | Recibe 200; un ID desconocido entrega 404 y la lista continúa protegida. |
| RF-005-03/04 | Proyecto válido con formset de recurso inválido | Se muestran errores y la base queda sin cambios parciales ni auditoría. |
| RF-005-03/13 | Edición cambia solo un integrante o recurso | Se confirma el conjunto y existe exactamente un evento `MODIFICAR`. |
| RF-005-05 | Se evalúa `str()` con archivo, URL o ambos | No hay `AttributeError` y el texto identifica el recurso. |
| RF-005-06 | Superusuario sin perfil edita/elimina | La vista lo autoriza y las plantillas renderizan sin error. |
| RF-005-06 | Usuario autenticado sin perfil intenta editar | Recibe denegación controlada y no se modifica el proyecto. |
| RF-005-07 | Se carga el inicio y se revisan recursos | No hay referencias a ECharts ni a `grafico_home.js`. |
| RF-005-08 | Se ejecutan las suites previstas | Cada app contiene casos reales; no se informa cobertura por ejecutar cero pruebas. |
| RF-005-09 | Se ejecuta `py manage.py tailwind build` | Termina correctamente y conserva clases usadas en `mensajes.js` y formularios Python. |
| RF-005-10 | Se consulta Git tras generar una migración | Los `.py` de migración aparecen como versionables y caches siguen ignoradas. |
| RF-005-11 | RESTRICTED autenticado abre usuarios | Ve el listado, pero no puede activar/desactivar/crear por URL directa. |
| RF-005-12 | Usuario autenticado sin cargo crea un proyecto válido | El proyecto se guarda con autor y un evento `CREAR`. |
| RF-005-13/14 | ADMIN/MANAGER o superusuario elimina | El proyecto desaparece y queda un evento `ELIMINAR` con snapshots y actor. |
| RF-005-15 | Se ejecuta la suite de dendrómetros | No aparecen regresiones atribuibles al cambio transversal. |

## Requisitos no funcionales

- La auditoría se escribe en servidor y participa de la misma atomicidad que la operación registrada.
- Las páginas públicas no añaden datos personales ni telemetría más allá del detalle ya publicado.
- Los mensajes de validación siguen en español y preservan la información ingresada cuando es seguro hacerlo.
- No se añade una consulta por evento durante los listados públicos ni una dependencia nueva.
- La compilación de estilos debe ser reproducible con el comando Django acordado.

## Compatibilidad

- Se conservan nombres de URL y destinos de QR existentes.
- Se conservan medios y campos de auditoría básica ya presentes en `Proyecto`.
- La corrección de atomicidad no cambia las validaciones de formato/tamaño ni las políticas de reemplazo de archivos.
- Las specs 001–004 continúan como baseline histórica; esta spec registra el cambio posterior.
- La migración de auditoría debe depender de la última migración real de `ProyectosApp`, una vez incorporada al control de versiones.

## Supuestos y decisiones pendientes

- **Interpretación aplicada a O-001:** “con los espacios igual” confirma las fichas y QR públicos descritos por la observación. Hacer pública la lista `/espacios/` no forma parte de esta spec.
- **Auditoría visible:** esta spec garantiza persistencia y pruebas, pero no crea una pantalla, API o exportación. Si se requiere consulta funcional, deben definirse actores y campos visibles antes de ampliar el alcance.
- **Representación de recurso:** el detalle exacto del texto es reversible; debe usar solo campos existentes y ser útil en admin/logs.
- No quedan decisiones críticas para documentar las correcciones. La implementación completa sigue pendiente de autorización posterior explícita.

## Revisión y cambios

- **2026-09-22:** creada a partir de la decisión del propietario sobre O-001 a O-010. No implica aprobación de la spec ni autorización de código.
- **2026-09-22:** el propietario revisó la spec y autorizó implementar todas las tareas. Implementación y validación registradas en `tasks.md` y `validation.md`.
