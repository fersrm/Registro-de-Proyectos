# Plan técnico retrospectivo — Spec 003

- **Estado:** Implementación existente, sin cambio autorizado.

`EspaciosApp` usa `ListView` con una colección en memoria, `TemplateView` para la ficha y una función de QR con un mapa de IDs a nombres de URL. Los assets y contenido viven en templates/static.

## Evolución posible

Si el número de espacios o editores crece, una futura spec puede proponer modelo, administración y migración de la entrada estática. Debe decidir antes qué campos son públicos y conservar URLs/QR existentes o definir redirecciones.

## Pruebas futuras

Acceso a lista, render de ficha, QR válido/404, contenido móvil y política pública. No hace falta crear persistencia mientras no exista requisito de edición dinámica.
