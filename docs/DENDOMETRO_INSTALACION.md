# DendometroApp — integración en la plataforma Django

## Qué se incorporó

El módulo convierte las funciones de la app Kivy en vistas de la plataforma. Usa el mismo motor de análisis de `processing.py`, adaptado para Django, y el diseño Tailwind/crispy_tailwind existente. No requiere Kivy, Matplotlib, Celery ni Redis.

- Menú **Dendrómetros · Visualización**: listado de sensores y monitor individual.
- Menú **Dendrómetros · Configuración**: alta y edición de sensores.
- Cada dendrómetro tiene su canal, campos, clave de lectura, calibración, ventanas, mantenimiento, umbrales y lecturas independientes.
- Histórico absoluto, detalle relativo con selector de sesión y señal cruda en tiempo real con mediana de 1 minuto.
- Última señal, último intervalo/última lectura operativa, cambio entre intervalos, amplitud, déficit, recuperación y tendencia.
- Exportaciones CSV de lecturas crudas anotadas y análisis completo de la ventana configurada.
- Alertas visuales y sonido activable con un clic. El navegador requiere interacción para habilitar audio.
- Carga inicial/manual con progreso y diálogo modal; refresco posterior en segundo plano.
- Importador de configuración y base SQLite de escritorio.
- Comando para descargar datos sin depender de una pestaña abierta.

## Aplicar sobre tu proyecto

Haz primero una copia de respaldo de tu proyecto y base de datos. Este ZIP conserva los archivos originales enviados; **no reemplaces tu base de datos ni tu `.env` de producción con los del ZIP**.

Desde la carpeta donde está `manage.py`, incorpora:

1. Carpeta nueva `DendometroApp/` completa.
2. Carpeta nueva `templates/dendometro/`.
3. Carpeta nueva `static/dendometro/` (incluye Chart.js local y su licencia).
4. Archivos nuevos `requirements_dendrometro.txt` y `docs/DENDOMETRO_*.md`.
5. En `core/settings.py`, añadir `"DendometroApp"` a `LOCAL_APPS`. Ya está aplicado en el ZIP.
6. En `core/urls.py`, añadir `path("dendrometros/", include("DendometroApp.urls"))`. Ya está aplicado.
7. Integrar los dos enlaces y la etiqueta de permisos añadidos a `templates/components/navbar/nav.html`. Ese menú se comparte entre móvil y escritorio.
8. En `templates/components/Layout/base.html`, se añadió un bloque `alpine_script` alrededor del script Alpine existente. Permite que el módulo use su copia local de Alpine sin depender del CDN para el menú móvil. Los demás módulos conservan su script anterior.
9. Usar el CSS Tailwind compilado de `theme/static/css/dist/styles.css`, o volver a compilarlo en tu entorno.

Si tu copia local cambió desde que enviaste el ZIP, fusiona los cambios de los pasos 5–8; no sustituyas a ciegas esos archivos compartidos. El resto de las apps no se modificó.

Activa tu entorno virtual y ejecuta:

```bash
python -m pip install -r requirements_dendrometro.txt
python manage.py migrate
python manage.py check
python manage.py runserver
```

En producción, además:

```bash
python manage.py collectstatic --noinput
```

Después recarga la aplicación/los workers del hosting. No se requiere generar migraciones: `DendometroApp/migrations/0001_initial.py` ya está incluida. No cambies DEBUG, credenciales o configuración HTTPS para instalar este módulo.

Para recompilar Tailwind, si lo necesitas:

```bash
python manage.py tailwind build
```

Los directorios de templates del módulo ya están cubiertos por el `tailwind.config.js` original. Las dependencias de Node deben instalarse en tu propio sistema si faltan.

## Primer sensor

1. Inicia sesión como superusuario o con cargo **ADMIN / MANAGER**.
2. Entra en **Dendrómetros · Configuración → Agregar dendrómetro**.
3. Indica nombre y ubicación. Puedes usar un nombre por árbol: `DC1 — Árbol 01`.
4. Introduce el Channel ID, Field 1 como señal y Field 2 como estado, si usas el firmware entregado.
5. Si el canal es público, deja la Read API Key vacía. Si es privado, usa su clave de **lectura**.
6. Selecciona `Milímetros (firmware actual)`, o pulsa **Cargar perfil ESP32 actual**.
7. Ajusta la ventana histórica y los parámetros; guarda.
8. Abre **Visualizar sensor**. La primera descarga mostrará su avance.

Para otro dendrómetro, repite el alta. Puede usar otro canal o campos distintos del mismo canal. Su configuración e historial no se comparten con el primero.

Después de guardar lecturas, no se permite cambiar el canal o los campos de origen de ese registro: crea otro dendrómetro para no reinterpretar un historial como si viniera de otro sensor. Sí puedes cambiar calibración y análisis: se recalculan sobre los valores crudos originales.

## Traer la app anterior

Conserva `dendrometer_config.json` y `dendrometer.db` de escritorio en una carpeta accesible al servidor. Ejecuta, adaptando las rutas:

```bash
python manage.py importar_dendrometro_escritorio "ruta/dendrometer_config.json" --nombre "DC1" --ubicacion "Parcela didáctica" --sqlite "ruta/dendrometer.db"
```

Sin `--sqlite`, importa solo la configuración. Cada ejecución crea un sensor nuevo; úsalo una vez por sensor. Valida el JSON antes de guardar y abre la base de escritorio en modo de solo lectura. No altera los archivos originales.

Las lecturas importadas conservan fecha UTC, valor y entry_id. La base original no almacenaba Field 2, por lo que esos registros tendrán estado desconocido hasta que la sincronización recupere las entradas disponibles en ThingSpeak. No se inventa ese dato.

Si el JSON anterior tiene mantenimiento abierto, se conserva. Para volver a operar, desactívalo en el formulario y guarda. Revisa las fechas históricas antes de hacerlo.

## Descarga sin navegador

Con la página abierta, el refresco automático realiza la sincronización. Si cierras todas las páginas, no queda un proceso en segundo plano salvo que programes este comando:

```bash
python manage.py sincronizar_dendrometros
```

Puedes programarlo mediante cron o las tareas de tu hosting. Usa el ejecutable Python del entorno virtual y la ruta completa a `manage.py`. La frecuencia real depende de las tareas disponibles en el hosting; no se ha creado ninguna tarea externa automáticamente.

Opciones:

```bash
python manage.py sincronizar_dendrometros --sensor 1
python manage.py sincronizar_dendrometros --sensor 1 --completo
python manage.py sincronizar_dendrometros --max-pasos 30
```

`--completo` vuelve a consultar toda la ventana configurada. `--max-pasos` permite limitar el trabajo de una ejecución; la siguiente continúa un trabajo pendiente. Deshabilitar un sensor evita nuevas descargas y conserva su historial.

## Cómo funciona la carga

ThingSpeak limita una consulta a 8.000 entradas. El módulo consulta rangos de hasta un día, del más reciente al más antiguo; si se alcanza el límite, divide ese rango y vuelve a consultarlo antes de considerarlo completo. Después guarda los valores crudos, sin reemplazarlos por promedios remotos.

El progreso mide la porción temporal de la ventana revisada, no una estimación inventada de segundos restantes. «Registros procesados» incluye coincidencias ya existentes; la restricción de sensor + fecha evita duplicarlas. Se informa si hubo entradas sin señal numérica válida.

Cada solicitud hace un paso corto. El estado del trabajo vive en la base de datos, así que puede reanudarse tras cerrar una página. Un bloqueo temporal evita que dos visitas ejecuten simultáneamente el mismo paso. Ante un error de red se conservan las lecturas ya guardadas; puedes repetir la descarga.

El diálogo bloquea la interacción con la página durante una carga manual. Los navegadores no permiten impedir que una persona cambie de pestaña, cierre el navegador o cambie de aplicación; se muestra un aviso y se solicita confirmación al intentar salir cuando el navegador lo permite.

Referencia del API: [MathWorks — Read Data](https://www.mathworks.com/help/thingspeak/readdata.html).

## Permisos y datos

- Visualización, CSV y actualización de lecturas: usuarios activos con sesión iniciada.
- Crear, editar y probar conexión: superusuario o cargo ADMIN / MANAGER, según `core.mixins.usuario_tiene_cargo`.
- Todos los usuarios autorizados a visualizar ven los sensores de la plataforma; no se implementó reparto por propietario o empresa.
- Las claves de ThingSpeak se usan en el servidor y no aparecen en los JSON del monitor. El campo de edición queda vacío: vacío conserva la clave; la casilla de eliminar la borra.
- Las operaciones que modifican datos usan POST y la protección CSRF de Django.
- El admin de Django ofrece consulta; el alta y los cambios se realizan mediante el formulario del módulo para aplicar las mismas validaciones.
- No hay borrado de sensores en la interfaz; deshabilitarlos conserva las lecturas.

## Verificación incluida

Para ejecutar las pruebas aisladas sin tocar la base de producción:

```bash
python manage.py test DendometroApp.tests --settings=DendometroApp.tests.settings
```

Las pruebas cubren cálculos, cortes de sesión, mantenimiento, aislamiento entre sensores, claves, permisos, CSRF, exportaciones, paginación, reintentos y exclusión mutua de descargas. Consulta `DENDOMETRO_VALIDACION.md` para el resultado de esta entrega.
