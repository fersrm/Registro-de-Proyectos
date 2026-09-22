# Dendrómetros web — uso y diferencias respecto a la app

## Visualización

El listado muestra nombre, ubicación, canal, intervalo, estado de mantenimiento/habilitación y última descarga. «Operativo» en el listado significa que el sensor está habilitado y no está marcado en mantenimiento; el monitor individual es el que diagnostica si las lecturas están atrasadas, son ceros o superan un umbral.

En el monitor puedes cambiar de sensor, actualizar manualmente, activar o desactivar el refresco, habilitar sonido y descargar CSV. La fecha de última descarga no es la fecha de última medición: una consulta exitosa puede devolver solo datos antiguos.

### Tarjetas

| Indicador | Cálculo / interpretación |
|---|---|
| Última señal recibida | Última lectura cruda convertida a µm, incluso si corresponde a pruebas o mantenimiento. |
| Último intervalo analizado | Último valor suavizado operativo. Durante mantenimiento se muestra en su lugar la última lectura cruda operativa de la ventana. |
| Cambio último intervalo | Último valor agregado − anterior, dentro de la misma sesión y solo si son intervalos consecutivos. Usa mediana/media por intervalo, sin suavizado. |
| Amplitud diaria | Máximo − mínimo de la curva suavizada del último día con datos, según la zona horaria del sensor. Necesita cobertura mínima dentro de ese día. |
| Déficit vs. máximo | Valor relativo actual − máximo acumulado de la curva suavizada en la sesión. Es ≤ 0. |
| Recuperación vs. máximo 24 h | Valor actual − máximo de los puntos anteriores de las últimas 24 h. Excluye el punto actual y puede ser positivo. |
| Tendencia lenta | Pendiente por ajuste lineal de la curva lenta en la ventana reciente; unidades µm/día. |

Ejemplo de intervalos de 30 min: 08:00 = 8500 µm, 08:30 = 8400 µm, 09:00 = 8570 µm. El cambio del último intervalo es **+170 µm**. El cambio acumulado respecto de 08:00 sería +70 µm; son magnitudes diferentes.

La tarjeta del intervalo conserva el cambio solicitado en la última app. Los umbrales bajo/alto siguen evaluando el cambio acumulado de la sesión, igual que el motor original; por eso el formulario los nombra explícitamente «cambio acumulado». No cambian de criterio silenciosamente.

El último intervalo puede estar en curso. Se indica cuando su mediana/media todavía puede variar. El suavizado es una mediana móvil centrada: los últimos puntos también pueden revisarse al llegar nuevos datos.

`—` significa que faltan datos para calcular o que la métrica está suspendida. No equivale a cero. Durante mantenimiento se ocultan las métricas actuales y se conservan el histórico y la señal electrónica.

### Coberturas

Los valores predeterminados son 12 h para amplitud/recuperación y 18 h para tendencia, con ventana de tendencia de 24 h.

La cobertura es la extensión entre timestamps dentro de la sesión, no una garantía de que exista una lectura en cada minuto. El criterio de recuperación conserva el motor original: requiere que la sesión alcance la duración mínima y compara al menos dos puntos previos dentro de 24 h. La tendencia necesita suficiente extensión entre valores de su curva lenta. Una sesión nueva puede tardar más que 18 h en producir una tendencia porque primero debe formarse la curva lenta.

### Gráficos

1. **Contexto histórico (mm):** posiciones absolutas por intervalo. Las sesiones se dibujan separadas y el último intervalo operativo se destaca. Puedes limitar la vista a 24 h, 7 días o toda la ventana. Este selector solo cambia el gráfico; las tarjetas siguen calculándose con la ventana configurada.
2. **Detalle relativo (µm):** cada sesión arranca en cero. Muestra intervalos, curva suavizada, envolvente y tendencia (si están activadas). Los umbrales acumulados se dibujan cuando están configurados. El selector permite revisar sesiones anteriores; las tarjetas siguen mostrando la última sesión y se advierte esa diferencia. Si la última sesión tiene solo un punto, se elige inicialmente la última con cambio calculable, igual que en escritorio.
3. **Tiempo real (µm):** señal cruda reciente más mediana de 1 minuto. Incluye datos excluidos para diagnóstico, marcados en gris. Un hueco largo rompe el trazo crudo.

Los gráficos grandes se reducen para el navegador; se muestra un aviso. El CSV y las métricas no utilizan esa reducción. Posición del sensor no significa diámetro total del árbol; la interpretación como circunferencia, radio o desplazamiento depende de cómo esté instalado y calibrado el dendrómetro.

## Sesiones

Una sesión es un tramo comparable de mediciones. Se abre otra cuando:

- El hueco entre intervalos supera el límite configurado (90 min de forma predeterminada).
- El salto entre intervalos supera el límite (1000 µm; 0 desactiva este criterio).
- Un período de mantenimiento separa los datos anteriores y posteriores.

No equivale necesariamente a conectar/desconectar físicamente el ESP32. Una caída de WiFi puede crear un hueco; una reinstalación puede provocar un salto. El suavizado y las métricas no cruzan estos cortes. Los números de sesión identifican los tramos dentro de la ventana consultada: pueden cambiar al ampliar o desplazar esa ventana.

Para impedir que un mismo intervalo mezcle posiciones antes y después de una reinstalación, se excluye del análisis cualquier intervalo que toque un mantenimiento. Los valores crudos permanecen guardados.

## Configuración por sensor

- **Identificación:** nombre, ubicación, descripción y habilitación para descargar.
- **ThingSpeak:** canal, campo de señal, campo de estado y Read API Key. La ventana histórica determina los días de análisis; la de tiempo real, las horas del gráfico crudo.
- **Tratamiento:** intervalo, media/mediana, mediana móvil, ventana de tendencia, corte por salto o por hueco, coberturas y exclusión de ceros.
- **Conversión:** con el firmware entregado, Field 1 ya contiene mm: la conversión es `mm × 1000`, seguida de factor y offset. Vex, ganancia y referencia solo se usan en modos de voltaje. El perfil ESP32 ajusta los parámetros de conversión y procesamiento; guarda para aplicarlos.
- **Mantenimiento:** activar abre un rango en UTC al guardar; desactivar cierra rangos abiertos. Puedes editar fechas históricas en el formato indicado. Los botones de inicio/fin marcan la opción y requieren guardar.
- **Alertas:** los umbrales fisiológicos en 0 están desactivados. Déficit y umbral bajo se escriben negativos; falta de recuperación y tendencia negativa se ingresan como magnitudes positivas. Ceros consecutivos, ausencia de datos y reajuste son avisos de diagnóstico.
- **Presentación:** envolvente, curva lenta y zona horaria. Las fechas crudas se almacenan en UTC; los gráficos y la amplitud diaria respetan la zona seleccionada.

Las alertas se priorizan: se muestra la condición principal, igual que en el motor de escritorio. Mantenimiento pausa las alarmas. El aviso de ceros sigue disponible aunque se excluyan los ceros de las métricas. El estado lógico de Field 2 es independiente: con el firmware entregado, 0 significa lectura menor a 0,5 mm y 1 significa mayor o igual a 0,5 mm; no confirma por sí solo si el sensor está conectado.

Los avisos sonoros se emiten en la página abierta después de activarlos. No son notificaciones por correo, SMS ni avisos del sistema operativo con la web cerrada.

## Diferencias de implementación

| Escritorio | Web |
|---|---|
| Configuración global en JSON | Configuración independiente por registro de dendrómetro. |
| SQLite local de lecturas | Tablas de la base Django de la plataforma. |
| Interfaz Kivy y gráficos Matplotlib | Templates Tailwind/crispy y gráficos interactivos Chart.js locales. |
| Ventana lateral | Página de configuración por sensor. |
| Refresco con hilo del proceso de escritorio | Peticiones cortas y trabajo reanudable guardado en la base. |
| Histórico agregado remoto cuando falta crudo local | Descarga por rangos de lecturas crudas; agregación y exclusiones en el servidor web. |
| Día de amplitud basado en UTC en el motor enviado | Día basado en la zona horaria configurable del sensor. |
| CSV guardado en la carpeta de la app | Descarga desde el navegador. |
| Dependencia de que la app esté abierta | Refresco con página abierta o comando programado en el servidor. |

No se cambia el firmware ni se escribe en ThingSpeak. No se incorporan automáticamente dispositivos o datos de prueba a tu base al aplicar las migraciones.
