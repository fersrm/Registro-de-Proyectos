# Instrucciones para agentes — Plataforma Agro

## Lectura inicial obligatoria

1. Lee `constitution.md`, `README.md`, `docs/PROYECTO.md`, `docs/ESTADO_PROYECTO.md` y `specs/README.md`.
2. Lee la spec afectada y solo las secciones necesarias de arquitectura, decisiones, observaciones y trazabilidad.
3. Inspecciona el código real y el estado de Git si existe. Conserva cambios del usuario y no dependas únicamente de conversaciones anteriores.

## Fases SDD

La fase predeterminada ante un módulo o cambio funcional es **DOCUMENTAR**:

1. `spec.md`: problema, actores, alcance, requisitos, datos, permisos y aceptación.
2. `plan.md`: solución propuesta, archivos reales, compatibilidad, riesgos, migraciones y estrategia de prueba.
3. `tasks.md`: tareas pequeñas, dependencias, RF asociados y condición de terminado.

En DOCUMENTAR solo se crean o actualizan Markdown. No crear apps, Python, HTML, JS, CSS, endpoints, migraciones, dependencias, pruebas ejecutables ni prototipos. Detenerse después de entregar los documentos. La implementación comienza únicamente cuando el usuario autoriza explícitamente la spec completa o tareas identificadas.

Usa `prompts/00-orquestador.md` para seleccionar las guías pertinentes. Encontrar un prompt no concede permiso para ejecutar otra fase. No entrevistar por rutina; dejar bloqueada la parte que dependa de una decisión crítica ausente.

## Línea base existente

No reconstruir estos módulos:

- `homeApp`: inicio autenticado, actividad reciente y resumen de proyectos.
- `UsuarioApp`: usuarios, perfiles, cargos, MFA/allauth y registro interno.
- `ProyectosApp`: proyectos, integrantes, recursos, imágenes y QR.
- `EspaciosApp`: catálogo y ficha de espacios con QR.
- `DendometroApp`: configuración, sincronización ThingSpeak, procesamiento, visualización y exportación.
- `theme`: Tailwind y layouts compartidos.

Las specs `001` a `004` describen la conducta observada. Son línea base retrospectiva, no una orden para reimplementar ni una garantía de que cada conducta sea deseada. El siguiente número libre es `005`, pero debe comprobarse antes de usarlo. Un ajuste pequeño actualiza la spec vigente; un módulo o cambio transversal obtiene carpeta nueva.

## Convenciones técnicas comprobadas

- Django 5.1, templates Django, vistas por clases como patrón predominante, Tailwind, crispy-tailwind y SQLite en desarrollo.
- Apps locales declaradas en `core/settings.py`; rutas en `core/urls.py`.
- Idioma `es-cl`, zona `America/Santiago`, `USE_TZ=True`.
- `usuario_tiene_cargo` admite superusuario y, para otros, exige usuario activo con perfil/cargo. `PermitsPositionMixin` autoriza ADMIN/MANAGER por defecto.
- El registro público está cerrado mediante `UsuarioApp.adapters.NoSignupAccountAdapter`; la creación interna usa `UserCreateView`.
- `preventconcurrentlogins` está activo. `django-axes` y correo real permanecen intencionalmente desactivados hasta que una spec autorice su configuración.
- No asumir que un enlace del menú representa el permiso real. Probar vista y método HTTP, incluidos acceso directo y usuario sin perfil.
- Mantener componentes y layouts existentes. Si Tailwind genera clases desde JS o Python, incluir esas rutas en `theme/static_src/tailwind.config.js` dentro de la implementación autorizada; hoy solo se escanean templates HTML.

## Reglas por área

### Dendrómetros

No exponer claves API ni configuración sensible. Mantener separadas lecturas crudas y análisis derivados, unidades explícitas, zonas horarias, intervalos excluidos y revisiones de configuración. Una sincronización debe conservar datos válidos ante error, evitar duplicados y respetar el aislamiento por sensor. Cambios matemáticos necesitan ejemplos y pruebas de regresión.

### Proyectos y archivos

Validar formato/tamaño en servidor y conservar la política de reemplazo/borrado de medios. Antes de cambiar páginas públicas o QR, definir matriz de exposición. Los formularios principal, integrantes y recursos deben persistir de forma atómica.

### Usuarios y navegación

Mantener coherencia entre helper, vista, plantilla y superusuario. Probar ADMIN, MANAGER, RESTRICTED, superusuario, usuario sin perfil y anónimo según el flujo. No reabrir registro público por accidente.

## Implementación, seguridad y datos

Implementar solo tareas autorizadas. No leer ni publicar secretos; no incluir `.env`, `db.sqlite3`, medios reales, `node_modules`, caches ni `staticfiles` en entregas. No desplegar, ejecutar migraciones en producción, hacer commit/push ni llamar servicios externos reales sin autorización específica.

Para errores: reproducir, comparar con el requisito, corregir la causa y añadir una regresión útil. No modificar la spec para declarar correcto el comportamiento defectuoso. Refactorizaciones extensas y actualizaciones de dependencias necesitan alcance propio.

## Comprobaciones

El dendrómetro dispone de configuración de pruebas aislada:

```bash
python manage.py test DendometroApp.tests --settings=DendometroApp.tests.settings --noinput
python manage.py check --settings=DendometroApp.tests.settings
python manage.py makemigrations --check --dry-run --settings=DendometroApp.tests.settings
```

Los demás `tests.py` recibidos son esqueletos; no reportar cobertura por ejecutar cero casos. Crear pruebas nuevas solo en fase de implementación autorizada. Si cambian estilos, desde `theme/static_src/` usar `npm ci` y `npm run build`. Una UI interactiva requiere navegador; un PDF o exportación visual requiere inspección apropiada.

Registrar comandos, resultados, límites y pendientes en la validación y el estado. Responder en español con cambios, evidencia y siguiente paso. La finalización técnica no equivale a aceptación del propietario.
