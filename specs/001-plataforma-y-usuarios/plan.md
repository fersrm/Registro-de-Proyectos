# Plan técnico retrospectivo — Spec 001

- **Estado:** Describe implementación existente; no propone reconstrucción.

## Componentes

- `core/settings.py`, `core/urls.py`, `core/mixins.py`.
- `UsuarioApp` para modelos, formularios y vistas.
- `homeApp` para inicio y middleware de actividad.
- `theme` y `templates/components/` para layout/navegación.
- allauth, MFA y preventconcurrentlogins como integraciones instaladas.

## Persistencia y seguridad

Auth estándar de Django más `Position`/`Profile`. El helper central debe ser la referencia para nuevas vistas. Secretos se cargan desde `.env`; archivos de perfil usan `MEDIA_ROOT`. Correo permanece en consola y axes inactivo.

## Estrategia de pruebas futura

Crear tests de adapter sin signup, matriz de cargos/superusuario/sin perfil, métodos POST y CSRF, activación/desactivación, búsqueda/paginación, perfil y throttling de actividad. Añadir pruebas de navegación solo como complemento; el servidor es la autoridad.

## Riesgos

Accesos directos a `user.profile.position_FK` pueden divergir del helper; el listado de usuarios está abierto a todo autenticado; el JS de gráfico referenciado no está presente.
