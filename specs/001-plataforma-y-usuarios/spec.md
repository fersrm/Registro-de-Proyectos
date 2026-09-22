# Spec 001 — Plataforma y usuarios

- **Estado:** Baseline documentada
- **Fecha de reconstrucción:** 2026-09-20
- **Fuente:** código recibido; no constituye aprobación funcional

## Objetivo observado

Proporcionar autenticación, MFA, perfiles/cargos, gestión interna de cuentas, actividad reciente, navegación compartida y base visual para los módulos Agro.

## Actores y permisos actuales

| Acción | Anónimo | RESTRICTED | MANAGER/ADMIN | Superusuario | Sin perfil |
|---|---:|---:|---:|---:|---:|
| Iniciar/cerrar sesión | Sí | Sí | Sí | Sí | Sí |
| Registro público | No | No | No | No | No |
| Ver inicio/listado de usuarios | No | Sí | Sí | Sí | Sí autenticado, con posibles diferencias de template |
| Crear/activar/desactivar usuarios | No | No | Sí | Sí | No salvo superusuario |
| Editar perfil propio | No | Sí | Sí | Sí | Se crea perfil si falta |

## Requisitos reconstruidos

- **RF-001-01:** el sistema exige autenticación para inicio, usuarios y perfil.
- **RF-001-02:** el registro público de allauth permanece cerrado y la creación interna requiere `PermitsPositionMixin`.
- **RF-001-03:** ADMIN, MANAGER y superusuario pueden crear, activar y desactivar cuentas; nadie puede desactivarse a sí mismo ni desactivar un superusuario.
- **RF-001-04:** el listado permite buscar por usuario/nombre/apellido, alternar activos/inactivos y pagina de nueve en nueve.
- **RF-001-05:** el usuario autenticado puede actualizar sus propios datos e imagen de perfil.
- **RF-001-06:** MFA TOTP y códigos de recuperación están disponibles mediante allauth.
- **RF-001-07:** el middleware actualiza actividad como máximo cada cinco minutos y el inicio considera activo al usuario visto dentro de diez minutos.
- **RF-001-08:** el inicio muestra hasta cinco usuarios activos con login reciente, cantidad y último proyecto.
- **RF-001-09:** el helper de cargos autoriza superusuario o perfil activo con código permitido; la autorización debe residir en servidor.
- **RF-001-10:** las sesiones simultáneas se limitan mediante `preventconcurrentlogins` según configuración actual.

## Exclusiones de la baseline

- Correo SMTP/verificación obligatoria.
- Activación de `django-axes`.
- Cambios al gráfico de ejemplo/archivo ausente.
- Garantía de que toda plantilla usa el helper central.

## Criterios de aceptación de la conducta documentada

- **CA-001-01:** un anónimo que solicita una vista interna es dirigido al login.
- **CA-001-02:** un intento de signup público es rechazado por el adapter configurado.
- **CA-001-03:** RESTRICTED no accede por URL directa a crear/activar/desactivar usuarios.
- **CA-001-04:** ADMIN/MANAGER/superusuario puede crear una cuenta con perfil válido.
- **CA-001-05:** desactivar la propia cuenta o un superusuario no cambia `is_active` y muestra error.
- **CA-001-06:** la actividad no escribe en cada petición dentro de la ventana de cinco minutos.

## Observaciones relacionadas

O-004, O-005, O-006, O-007 y O-009 en `docs/OBSERVACIONES_PROYECTO.md`.
