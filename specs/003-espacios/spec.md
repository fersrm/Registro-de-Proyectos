# Spec 003 — Espacios

- **Estado:** Baseline documentada
- **Fecha de reconstrucción:** 2026-09-20

## Objetivo observado

Presentar espacios agroeducativos mediante una lista interna y fichas simples accesibles por URL/QR.

## Estado actual

La lista se construye en `EspaciosListView` con un único registro estático, “Parcela Didáctica”; no existe modelo de persistencia. La lista requiere login. La ficha `espacio_1` y su QR son públicos.

## Requisitos reconstruidos

- **RF-003-01:** un usuario autenticado puede ver la lista con nombre, descripción, ubicación, superficie, imagen y enlace.
- **RF-003-02:** la ficha de Parcela Didáctica usa su template dedicado.
- **RF-003-03:** el endpoint QR acepta IDs conocidos, genera un PNG hacia la URL absoluta y responde 404 para un ID desconocido.
- **RF-003-04:** ficha y QR son públicos según el código actual.

## Criterios de aceptación

- **CA-003-01:** anónimo no accede a la lista.
- **CA-003-02:** autenticado abre el espacio configurado desde la lista.
- **CA-003-03:** el QR de `espacio_1` apunta a la ficha correcta.
- **CA-003-04:** ID no reconocido devuelve 404 sin generar QR.

## Exclusiones

- CRUD, base de datos, múltiples espacios configurables, mapa o inventario.
- Decisión de mantener exposición pública al incorporar nuevos datos.

## Observaciones relacionadas

O-001 y O-006.
