# Spec 004 — Dendrómetros

- **Estado:** Baseline documentada
- **Fecha de reconstrucción:** 2026-09-20
- **Documentación complementaria:** `LEEME_DENDOMETRO.md`, `docs/DENDOMETRO_FUNCIONAMIENTO.md`, `docs/DENDOMETRO_INSTALACION.md`, `docs/DENDOMETRO_VALIDACION.md`

## Objetivo observado

Configurar dendrómetros, importar lecturas desde ThingSpeak, conservar datos crudos y presentar análisis temporal confiable con sesiones, calibración, agregación, tendencia, alertas y exportación.

## Actores y permisos actuales

| Acción | Anónimo | Usuario activo | ADMIN/MANAGER/superusuario |
|---|---:|---:|---:|
| Lista, visualización y datos | No | Sí | Sí |
| Iniciar/avanzar sincronización | No | Sí | Sí |
| Exportar CSV crudo/analizado | No | Sí | Sí |
| Crear/editar/probar configuración | No | No | Sí |

## Datos principales

- `Dendrometro`: identidad, ubicación, estado, canal/campos ThingSpeak, clave de lectura, configuración JSON, revisión y estado de última sincronización.
- `Lectura`: sensor, timestamp, entry ID, señal/valor float y estado; unicidad por sensor/timestamp.
- `Sincronizacion`: trabajo UUID, sensor/revisión, rango, avance, errores y lease; una pendiente por sensor.

## Requisitos reconstruidos

- **RF-004-01:** cada sensor mantiene configuración independiente y una revisión que protege trabajos frente a cambios.
- **RF-004-02:** la clave de ThingSpeak permanece en servidor, puede conservarse o limpiarse explícitamente y nunca aparece en payloads/páginas.
- **RF-004-03:** configuración valida intervalos, agregación, suavizado, sesiones, cobertura, calibración, alertas, display y zona horaria.
- **RF-004-04:** la sincronización usa HTTPS, timeout, rangos, paginación/división ante límite y parsing de numéricos válidos.
- **RF-004-05:** repetir/importar concurrentemente no duplica lecturas; trabajos y lease están aislados por sensor.
- **RF-004-06:** un fallo remoto conserva lecturas válidas y permite reintento; GET no produce sincronización y los cambios requieren CSRF/POST.
- **RF-004-07:** datos crudos no se convierten destructivamente; calibración genera valores derivados en µm según modo configurado.
- **RF-004-08:** mantenimiento, huecos y saltos separan sesiones; un intervalo de consulta por sí solo no crea una sesión falsa.
- **RF-004-09:** agregación por defecto es de 30 minutos y puede usar mediana/media; suavizado/tendencia no inventan continuidad a través de sesiones.
- **RF-004-10:** métricas, delta, amplitud diaria, señal reciente/obsoleta, ceros y alertas consideran zona horaria, cobertura y exclusiones configuradas.
- **RF-004-11:** la visualización reduce registros para cliente sin perder acceso a exportación cruda/analizada.
- **RF-004-12:** es posible importar configuración/lecturas compatibles desde fuentes de escritorio previstas por los servicios existentes.

## Casos de aceptación representativos

- **CA-004-01:** una señal se convierte exactamente una vez y la lectura cruda permanece disponible.
- **CA-004-02:** intervalo faltante no produce delta; gap, mantenimiento o salto crean nueva sesión.
- **CA-004-03:** dos clientes sobre el mismo trabajo respetan lease y no duplican datos.
- **CA-004-04:** respuesta saturada se divide sin declarar completo el rango antes de tiempo.
- **CA-004-05:** NaN/valores inválidos se descartan y se usa el campo de estado seleccionado.
- **CA-004-06:** cambiar una fuente tras almacenar lecturas incompatibles se rechaza.
- **CA-004-07:** usuario activo puede analizar/sincronizar/exportar, pero solo cargo autorizado configura.
- **CA-004-08:** HTML/JSON no contienen API key.

## Límites actuales

- La integración real depende de ThingSpeak y de credenciales/entorno no incluidos.
- Las pruebas recibidas usan dobles para red; no certifican disponibilidad remota.
- La validez agronómica de umbrales/configuración requiere revisión del dominio.
