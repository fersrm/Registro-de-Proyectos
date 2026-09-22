# Proyecto

## Identidad

- **Nombre de trabajo:** Plataforma Agro.
- **Estado:** producto Django existente, en evolución incremental.
- **Propósito observado:** centralizar proyectos e información de espacios agroeducativos, administrar usuarios internos y visualizar datos de dendrómetros sincronizados desde ThingSpeak.
- **Idioma/zona:** español de Chile; `America/Santiago`.

## Usuarios observados

- **ADMIN:** administración funcional según vistas protegidas por cargo.
- **MANAGER:** administración operativa según las mismas vistas protegidas.
- **RESTRICTED:** usuario autenticado con acceso más acotado; puede existir autoría propia en proyectos.
- **Superusuario:** autorizado por el helper central, aunque algunas plantillas/vistas acceden al perfil directamente y pueden diferir.
- **Anónimo:** login/allauth y páginas públicas actuales de detalle/QR de proyectos y espacios.

## Capacidades actuales

1. Inicio autenticado con últimos accesos, actividad y resumen de proyectos.
2. Gestión interna de usuarios y perfiles; MFA disponible; registro público cerrado.
3. Catálogo de proyectos con integrantes, recursos, imágenes, búsqueda y QR.
4. Catálogo estático de espacios y ficha pública mediante QR.
5. Dendrómetros configurables, sincronización ThingSpeak, procesamiento, métricas, alertas, gráficos y CSV.

## Fuera del alcance de esta línea base documental

- Cambiar comportamiento funcional, corregir observaciones o crear migraciones.
- Activar correo real o `django-axes`.
- Desplegar o modificar datos productivos.
- Certificar privacidad, seguridad, exactitud agronómica o capacidad de producción.

## Cambio transversal implementado — Spec 005

El 2026-09-22 el propietario confirmó que:

- detalle y QR de proyectos, y fichas y QR de espacios, continúan públicos sin login;
- el listado de usuarios continúa disponible para cualquier usuario autenticado, no para anónimos;
- cualquier usuario autenticado puede crear proyectos; y
- crear, modificar y eliminar proyectos debe dejar auditoría persistente.

La spec 005 corrigió atomicidad de formularios de proyectos, `RecursoProyecto.__str__`, permisos inconsistentes, el gráfico de ejemplo ausente, pruebas de apps, fuentes Tailwind y versionado de migraciones. La validación automatizada y visual está registrada en `specs/005-correcciones-observaciones-y-auditoria/validation.md`; la aceptación final del propietario continúa pendiente.

Como ajuste pequeño posterior, los controles de cierre de sesión de la barra lateral y menú de perfil ejecutan `POST` con CSRF directamente, sin pantalla de confirmación y sin habilitar logout por `GET`.

## Fuentes

Código del ZIP recibido el 2026-09-20, specs `001`–`005`, `LEEME_DENDOMETRO.md` y documentación `DENDOMETRO_*` existente.
