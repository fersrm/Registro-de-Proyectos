# Plan técnico — Spec 005: correcciones de observaciones y auditoría

Spec: [spec.md](spec.md). Estado: implementado y validado.
Autorización de implementación: recibida el 2026-09-22; aceptación final pendiente.

## Inspección de la base

Se contrastaron `constitution.md`, documentación SDD, specs 001–004 y el código real de `core`, `homeApp`, `UsuarioApp`, `ProyectosApp`, `EspaciosApp`, `DendometroApp`, `theme` y templates compartidos.

Hallazgos que determinan el plan:

- `ProyectoCreateView` y `ProyectoUpdateView` guardan el objeto principal antes de validar ambos formsets y retornan desde `transaction.atomic()` sin provocar rollback.
- `RecursoProyecto.__str__()` llama `get_tipo_display()` sin existir un campo `tipo`.
- `ProyectoUpdateView` y varias plantillas acceden directamente a `profile.position_FK`, mientras `usuario_tiene_cargo` contempla superusuario, usuario inactivo y perfil ausente.
- `templates/pages/index.html` incluye ECharts y `static/js/grafico_home.js`; el archivo no existe y no hay gráfico usado por la página.
- `homeApp/tests.py`, `UsuarioApp/tests.py`, `ProyectosApp/tests.py` y `EspaciosApp/tests.py` son esqueletos.
- `static/js/mensajes.js` contiene clases Tailwind y `UsuarioApp/forms.py` construye clases en Python, pero la configuración solo escanea HTML.
- `.gitignore` ignora cualquier carpeta `migrations/`; las migraciones locales existen en disco pero ninguna está versionada.
- `Proyecto` ya conserva creador, último modificador y fechas, pero no existe un evento que sobreviva a una eliminación.
- El árbol de trabajo tenía un cambio previo en `db.sqlite3`; debe permanecer intacto y fuera de la entrega.

## Diseño propuesto

### 1. Operación atómica de proyecto

Reestructurar los flujos de alta y edición para construir los formsets con la instancia adecuada, validar formulario y formsets antes de confirmar, y guardar proyecto, integrantes, recursos y evento de auditoría dentro de una única transacción. No se debe llamar de nuevo al guardado estándar de `CreateView`/`UpdateView` de forma que duplique escrituras o eventos.

Los archivos nuevos cargados durante una transacción fallida requieren una revisión específica: la base de datos puede revertir filas, pero el almacenamiento de archivos no es transaccional. La implementación debe evitar guardar formsets inválidos y cubrir la política existente de reemplazo/borrado; no se autoriza borrar medios ajenos al intento actual.

### 2. Auditoría persistente

Ampliar `ProyectosApp` con un modelo `AuditoriaProyecto` (nombre final reversible) que almacene acción, fecha, referencia opcional al proyecto vivo, snapshots mínimos del proyecto y referencia/snapshots del actor. Sus eventos se crean explícitamente desde los casos de uso exitosos de crear, modificar y eliminar.

No se propone señal global: las vistas necesitan coordinar el evento con los formsets y la transacción, y una señal podría registrar operaciones parciales o duplicar eventos. Tampoco se propone un paquete externo.

La eliminación se envuelve en una transacción. El evento se prepara con los datos del objeto antes del borrado y debe sobrevivirlo mediante `SET_NULL` y snapshots. No se añade interfaz pública ni exportación de auditoría.

### 3. Política común de permisos

Mantener `core.mixins.usuario_tiene_cargo` como autoridad para ADMIN/MANAGER/superusuario. Agregar una forma segura y reutilizable de evaluar permisos desde templates, preferentemente un template tag que delegue en el helper, y una comprobación segura para RESTRICTED propietario.

Aplicar la misma política a `ProyectoUpdateView`, navegación, inicio, listado de usuarios y controles de proyectos. Las vistas siguen siendo la barrera real; la plantilla solo refleja el permiso. Superusuario sin perfil queda autorizado; usuario sin perfil no obtiene cargo ni provoca excepciones.

### 4. Estáticos y Tailwind

Retirar de `templates/pages/index.html` las dos etiquetas del gráfico de ejemplo: ECharts remoto y `grafico_home.js`. No hay archivo físico que borrar.

Añadir a `theme/static_src/tailwind.config.js` globs específicos para JavaScript propio y Python con clases reales, excluyendo `node_modules`, `.venv`, artefactos y librerías empaquetadas. La comprobación de estilos se realiza con:

```powershell
py manage.py tailwind build
```

### 5. Migraciones versionables

Eliminar la regla global `migrations/` de `.gitignore` y conservar las reglas de `__pycache__`/`*.pyc`. Incorporar primero las migraciones locales históricas que hoy están ignoradas y luego generar la migración de auditoría desde la última dependencia real de `ProyectosApp`. No ejecutar migraciones sobre producción ni incluir `db.sqlite3`.

### 6. Suites por app

Sustituir los esqueletos por paquetes o módulos de pruebas organizados por flujo. Reutilizar factories/helpers mínimos locales si reducen duplicación, sin crear una infraestructura ajena a Django. Las pruebas de red de dendrómetros continúan usando dobles; no se llama ThingSpeak real.

## Mapa por requisito

| RF | Archivos existentes / propuestos | Cambio previsto | Evidencia prevista |
|---|---|---|---|
| RF-005-01 | `ProyectosApp/views.py`, `urls.py`; tests propuestos | Conservar detalle/QR públicos y probar 200/404/destino. | Cliente anónimo y lectura del QR o URL construida. |
| RF-005-02 | `EspaciosApp/views.py`, `urls.py`; tests propuestos | Conservar ficha/QR públicos y lista autenticada. | Casos anónimo/autenticado y QR desconocido. |
| RF-005-03/04 | `ProyectosApp/views.py`, `forms.py`; tests propuestos | Validación previa y una sola transacción para principal/formsets/auditoría. | Conteos y valores sin cambios tras entradas inválidas. |
| RF-005-05 | `ProyectosApp/models.py` | Corregir `__str__` con campos existentes. | Pruebas con archivo, URL y ambos. |
| RF-005-06 | `core/mixins.py`, `ProyectosApp/views.py`, templates; nuevo `UsuarioApp/templatetags/` | Helper/tag seguro compartido y matriz coherente. | Casos ADMIN, MANAGER, RESTRICTED, superusuario, sin perfil y anónimo. |
| RF-005-07 | `templates/pages/index.html` | Retirar ECharts y referencia inexistente. | Render y búsqueda sin ambos recursos. |
| RF-005-08 | `homeApp/tests/`, `UsuarioApp/tests/`, `ProyectosApp/tests/`, `EspaciosApp/tests/` propuestos | Suites funcionales reales por módulo. | Comandos de prueba con casos ejecutados. |
| RF-005-09 | `theme/static_src/tailwind.config.js` | Globs específicos para `static/js` y Python local con clases. | Build Django y revisión de CSS generado/UI. |
| RF-005-10 | `.gitignore`, migraciones locales existentes y nueva migración propuesta | Versionar cadena histórica y auditoría. | `git check-ignore`, `makemigrations --check --dry-run`. |
| RF-005-11 | `UsuarioApp/views.py`, templates y tests | Preservar listado para autenticados y acciones solo por cargo. | Matriz de GET/POST y URL directa. |
| RF-005-12/13/14 | `ProyectosApp/models.py`, `views.py`, `admin.py` solo si se autoriza consulta técnica, migración y tests | Modelo/eventos transaccionales con snapshots. | Eventos exactos y persistencia después de borrar proyecto/actor. |
| RF-005-15 | `DendometroApp/tests/` existente | Sin cambio funcional; ejecutar regresión aislada. | Suite y checks de dendrómetro. |

## Datos y contratos

El modelo de auditoría propuesto usa:

- `accion`: `CharField` con choices cerradas;
- `fecha`: `DateTimeField(auto_now_add=True)`;
- `proyecto`: FK nullable con `SET_NULL`, sin cascade sobre el evento;
- `proyecto_id_original` y `proyecto_titulo`: snapshots obligatorios;
- `actor`: FK nullable a `User` con `SET_NULL` y `related_name` propio;
- `actor_id_original` nullable y `actor_username`: snapshots históricos.

Los campos snapshot se completan en servidor y no forman parte de formularios. La creación de eventos debe ocurrir exactamente una vez por operación lógica confirmada. No se backfillean eventos para datos anteriores.

No cambian los contratos de las URLs públicas ni los formatos de QR. Los POST de acciones administrativas conservan CSRF y las vistas no convierten acciones mutables en GET.

## Permisos e interfaz

- El detalle público debe renderizar de forma segura con `AnonymousUser` y con usuarios sin perfil.
- Los controles de crear, editar, eliminar, registrar, activar y desactivar reflejan el helper común.
- El listado de usuarios conserva login obligatorio para proteger emails y datos de cuenta de visitantes anónimos.
- No se añade navegación a la auditoría en este cambio.
- Tras tocar templates/estilos se revisan vistas de escritorio y móvil de inicio, usuarios, proyectos y espacios.

## Migraciones y reversión

1. Incorporar al control de versiones las migraciones históricas existentes de `UsuarioApp`, `ProyectosApp` y `DendometroApp`, además de los `__init__.py` correspondientes.
2. Verificar que la base de desarrollo actual reconoce su historial antes de generar archivos nuevos.
3. Crear una migración aditiva para `AuditoriaProyecto`, sin alterar ni borrar datos existentes.
4. Ejecutar únicamente en entorno local/de prueba `makemigrations --check --dry-run` y las pruebas.
5. No aplicar migraciones en producción en esta tarea.

La reversión de código puede dejar la tabla de auditoría sin consumidores; eliminarla destruiría historial y requiere una decisión y respaldo separados. Por ello no se propone una migración destructiva automática de reversión.

## Plan de pruebas

### Proyectos

- formularios válidos y cada formset inválido por separado;
- ausencia de persistencia parcial en creación y edición;
- archivos/URLs, tamaños/extensiones y reemplazo de imágenes;
- `__str__` de recursos;
- matriz de lista, detalle, QR, crear, editar y eliminar;
- superusuario y usuario sin perfil;
- un evento exacto por crear/modificar/eliminar, ninguno ante rollback;
- supervivencia del evento tras borrar proyecto y, mediante caso aislado, actor;
- búsqueda y URLs existentes como regresión.

### Usuarios e inicio

- login requerido para inicio/listado y signup público cerrado;
- listado para RESTRICTED, ADMIN, MANAGER, superusuario y sin perfil;
- POST de crear/activar/desactivar protegido por cargo, incluida URL directa;
- perfil propio y creación de perfil ausente;
- resumen de proyectos, actividad reciente y throttling del middleware;
- render seguro de navegación y páginas con perfiles ausentes.

### Espacios

- lista autenticada;
- ficha y QR públicos;
- QR válido y 404 desconocido;
- destino correcto del QR.

### Tailwind y validación transversal

Comandos previstos, no ejecutados en DOCUMENTAR:

```powershell
py manage.py test homeApp UsuarioApp ProyectosApp EspaciosApp --noinput
py manage.py test DendometroApp.tests --settings=DendometroApp.tests.settings --noinput
py manage.py check
py manage.py check --settings=DendometroApp.tests.settings
py manage.py makemigrations --check --dry-run
py manage.py makemigrations --check --dry-run --settings=DendometroApp.tests.settings
py manage.py tailwind build
```

Después del build se requiere inspección en navegador de los flujos tocados. Los resultados reales irán en `validation.md`; no se declarará cobertura por suites vacías ni por una ejecución que no comenzó.

## Riesgos, alternativas y dependencias

- El almacenamiento de archivos no revierte automáticamente junto con la base de datos; la implementación debe evitar huérfanos del intento fallido y probar reemplazos.
- Versionar por primera vez migraciones existentes exige revisar dependencias y estado aplicado antes de generar la nueva; no se debe recrear `0001` ni falsear el historial.
- Un glob Python demasiado amplio puede escanear `.venv`; se prefieren rutas explícitas de apps/archivos locales.
- Las plantillas con helpers divergentes pueden mostrar controles incorrectos aun cuando el servidor deniegue; deben migrarse como conjunto y probarse.
- Usar señales para auditoría simplificaría algunos llamados, pero dificulta garantizar un evento por operación lógica con formsets; se descarta para este alcance.
- Una bitácora con diffs completos aumentaría datos personales y complejidad; se elige evento mínimo porque el pedido es identificar quién y cuándo.

## Documentos afectados

- `specs/README.md`: registrar spec 005 y siguiente número libre.
- `docs/PROYECTO.md`: registrar las políticas confirmadas y cambio propuesto.
- `docs/ESTADO_PROYECTO.md`: dejar punto de reanudación y autorización pendiente.
- `docs/DECISIONES.md`: conservar decisiones confirmadas de acceso, creación, auditoría y build.
- `docs/TRAZABILIDAD.md`: mapear la propuesta y evidencia prevista.
- `docs/ARQUITECTURA.md`: marcar auditoría y permisos comunes como arquitectura propuesta, no implementada.

## Ajuste pequeño posterior — cierre de sesión directo

Los enlaces de cierre de sesión de la barra lateral y el menú de perfil se sustituyen por formularios `POST` con `{% csrf_token %}` hacia `account_logout`. Así, el usuario cierra sesión en un único clic y allauth no necesita renderizar su pantalla de confirmación. Se conserva `ACCOUNT_LOGOUT_ON_GET = False`; no hay cambios de configuración, rutas, permisos ni datos.

Por instrucción expresa del propietario no se ejecutan pruebas adicionales para este ajuste. La comprobación se limita a inspección estática de ambos formularios y de la configuración de logout.

## Decisiones para implementar

No apareció un vacío crítico durante la implementación. La lista pública de espacios y una interfaz de consulta de auditoría permanecen fuera de alcance hasta una decisión explícita. Los resultados y límites reales constan en `validation.md`.
