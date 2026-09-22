# Arquitectura actual

## Vista general

| Capa | Componentes |
|---|---|
| Configuración | `core/settings.py`, `core/urls.py`, `core/mixins.py` |
| Presentación | Django Templates, Tailwind (`theme`), JS/CSS estático |
| Identidad | auth de Django, django-allauth, MFA, `UsuarioApp`, preventconcurrentlogins |
| Negocio | `ProyectosApp`, `EspaciosApp`, `DendometroApp`, `homeApp` |
| Datos | ORM de Django; SQLite configurado en desarrollo |
| Integración | API de lectura ThingSpeak vía servicios del dendrómetro |

## Apps

- `homeApp`: inicio y actualización periódica de `last_activity`.
- `UsuarioApp`: cargos, perfiles, creación interna, listado y activación.
- `ProyectosApp`: proyecto, integrantes y recursos; archivos bajo `media/proyectos/`.
- `EspaciosApp`: lista construida en código y detalle de parcela sin modelo persistente.
- `DendometroApp`: modelos de sensor, lectura y trabajo de sincronización; servicios separados de configuración, API, procesamiento y análisis.
- `theme`: compilación Tailwind y plantilla base.

## Acceso actual resumido

| Área | Anónimo | Autenticado | ADMIN/MANAGER/superusuario |
|---|---:|---:|---:|
| Inicio/listado de usuarios | No | Sí | Sí |
| Crear/activar/desactivar usuarios | No | No por defecto | Sí |
| Lista/crear proyectos | No | Sí | Sí |
| Editar proyecto | No | Creador RESTRICTED según código | Sí por cargo; revisar superusuario sin perfil |
| Eliminar proyecto | No | No | Sí |
| Detalle/QR proyecto | Sí | Sí | Sí |
| Lista de espacios | No | Sí | Sí |
| Ficha/QR de espacio | Sí | Sí | Sí |
| Ver/sincronizar/exportar dendrómetro | No | Usuario activo | Sí |
| Configurar dendrómetro | No | No por defecto | Sí |

Esta tabla registra conducta observada; no afirma que la exposición pública sea la política final.

## Dendrómetro

Las lecturas crudas se persisten por sensor y marca temporal. La configuración JSON se interpreta en servicios; análisis y gráficos derivan valores convertidos, sesiones, suavizado, tendencia y alertas. La sincronización usa trabajos persistentes, rangos y lease para reanudación/concurrencia. ThingSpeak se consulta por HTTPS desde servidor y la clave no debe llegar al navegador.

## Cambios implementados

### Spec 005 — implementada y validada el 2026-09-22

- `ProyectosApp` incorpora `AuditoriaProyecto` para eventos mínimos de crear, modificar y eliminar. Los eventos participan de la transacción de negocio y conservan snapshots de actor/proyecto después de eliminaciones.
- Las vistas de proyectos validan formulario principal y formsets antes de confirmar una sola transacción.
- `core.mixins.usuario_tiene_cargo` es la autoridad para ADMIN/MANAGER/superusuario y `permisos_tags` reutiliza la regla en la interfaz.
- Tailwind escanea rutas específicas de JavaScript y Python propias que contienen clases, sin recorrer entornos ni dependencias.
- Las migraciones de apps locales están disponibles para control de versiones y la auditoría se añade mediante `ProyectosApp.0009`.

La interfaz pública de consulta de auditoría y hacer pública la lista de espacios no forman parte de la arquitectura implementada.
