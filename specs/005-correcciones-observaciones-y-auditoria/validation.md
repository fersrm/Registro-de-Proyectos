# Validación — Spec 005

- **Fecha:** 2026-09-22
- **Estado:** implementación validada; aceptación del propietario pendiente
- **Datos usados:** usuarios, proyecto y SQLite sintéticos; sin servicios externos ni datos reales
- **Producción:** no modificada

## Resultado

Se implementaron O-002 a O-008 y las políticas confirmadas de O-001, O-009 y O-010. La auditoría de proyectos, atomicidad, permisos, migraciones versionables, recursos estáticos y suites por app cumplen los casos automatizados y la revisión visual prevista.

## Cambios comprobados

- `Proyecto`, integrantes, recursos y auditoría se confirman en una sola transacción.
- Un formset inválido no persiste el principal ni un evento; un fallo simulado de auditoría revierte la creación completa.
- Crear, modificar y eliminar produce exactamente el evento esperado con snapshots; el evento sobrevive al borrado del proyecto y del actor.
- ADMIN/MANAGER/superusuario comparten la política central; RESTRICTED solo edita lo propio y un usuario sin perfil no obtiene permisos ni provoca error.
- Detalle/QR de proyecto y ficha/QR de espacio siguen públicos; los listados conservan login.
- El listado de usuarios admite cualquier autenticado y mantiene acciones administrativas protegidas.
- El inicio ya no carga ECharts ni `grafico_home.js`.
- Tailwind escanea `static/js/**/*.js` y Python de `UsuarioApp`, excluyendo migraciones y dependencias.
- Las migraciones locales dejaron de estar ignoradas y `0009_auditoriaproyecto.py` es aditiva.
- El importador SQLite de dendrómetros y su fixture cierran handles explícitamente en Windows; no se alteró procesamiento ni datos del módulo.

## Evidencia automatizada

El lanzador `py` y el ejecutable de `.venv/Scripts/python.exe` no funcionan en este host. Para no tocar `db.sqlite3`, se utilizó Python 3.12.14 del runtime aislado de Codex, agregando únicamente los paquetes ya instalados en `.venv/Lib/site-packages` (Django 5.1.2), y `DendometroApp.tests.settings` con SQLite en memoria.

| Comprobación real | Resultado |
|---|---|
| Tests conjuntos de `homeApp`, `UsuarioApp`, `ProyectosApp`, `EspaciosApp` y `DendometroApp.tests` | **53/53 OK** en 0,655 s; base en memoria creada y destruida |
| `check` con configuración estándar | **0 problemas** |
| `check` con `DendometroApp.tests.settings` | **0 problemas** |
| `makemigrations --check --dry-run` estándar | **No changes detected** |
| `makemigrations --check --dry-run` aislado | **No changes detected** |
| Tailwind CLI local con Node y paquetes existentes | **OK**, `Done in 638ms` |
| Clases generadas desde fuentes dinámicas | Se verificaron `hover:text-red-500`, `focus:outline-none` y `appearance-none` en el CSS final |
| `git diff --check` | Sin errores de whitespace; avisos esperados CRLF/LF en Windows |

El build final equivalente ejecutado, desde `theme/static_src`, fue:

```powershell
& '<runtime-node>\node.exe' .\node_modules\tailwindcss\lib\cli.js --postcss -i .\src\styles.css -o ..\static\css\dist\styles.css --minify
```

El intento de usar el gestor `pnpm` del runtime no se aceptó como evidencia: quiso convertir `node_modules` y acceder a red. Se detuvieron sus procesos, se restauraron los paquetes movidos y se eliminaron sus carpetas temporales antes del build offline final. No se actualizaron dependencias.

## Validación visual

Se levantó un servidor local con base SQLite sintética separada, eliminado al terminar. Se inspeccionó mediante navegador:

- detalle público de proyecto sin login;
- inicio autenticado sin bloque de gráfico ni solicitudes asociadas;
- listado de proyectos con crear/editar/eliminar para superusuario sin perfil;
- listado de usuarios con controles administrativos y etiqueta “Superusuario”;
- formulario de proyecto y navegación;
- escritorio a 1440×900 y móvil a 390×844.

No se observaron desbordes horizontales, errores de template ni controles incoherentes en las pantallas revisadas. El servidor, usuario sintético y base visual fueron retirados al finalizar.

## Límites y pendientes

- El ajuste posterior de cierre de sesión directo se implementó como `POST` con CSRF en los dos controles de navegación. Por instrucción expresa del propietario no se ejecutaron pruebas adicionales para este ajuste pequeño.

- No se pudo ejecutar literalmente `py manage.py tailwind build` porque Windows informó `No installed Python found`; el README conserva ese comando como vía oficial del proyecto. Debe repararse el Python Launcher o recrearse `.venv` para repetirlo de forma literal en este equipo.
- Tailwind avisó que `caniuse-lite` está desactualizado. No se actualizó porque las dependencias están fuera del alcance.
- No se aplicó `0009_auditoriaproyecto` a `db.sqlite3` ni a producción.
- No se probó ThingSpeak real ni se usaron secretos.
- La lista pública de espacios y una interfaz de consulta de auditoría siguen fuera del alcance acordado.
- La aceptación funcional del propietario permanece pendiente.
