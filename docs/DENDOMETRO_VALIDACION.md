# Verificación de la entrega

## Resultado

- `manage.py check`: sin incidencias.
- `makemigrations DendometroApp --check --dry-run`: sin cambios pendientes.
- Suite `DendometroApp.tests`: **26 pruebas aprobadas**.
- Sintaxis JavaScript: comprobada con `node --check`.
- Tailwind: CSS compilado e incluido.
- Django + navegador Chromium: visualización, edición y guardado de formularios, selección de sesiones, vista tiempo real, sensores sin datos y navegación móvil comprobados.
- Pantalla móvil de 390 px: ancho del documento 390 px, sin desbordamiento horizontal.
- El navegador no registró errores JavaScript en el recorrido del módulo.
- Progreso, diálogo modal, aviso de éxito y recuperación tras un error: comprobados en navegador con respuestas simuladas.

## Cobertura de las pruebas

Conversión mm a µm; diferencia entre intervalo y sesión; intervalos faltantes; sesiones por hueco, salto y mantenimiento breve; amplitud por zona horaria; tendencia reciente; permisos ADMIN/MANAGER/lector; páginas del módulo; separación de lecturas y configuraciones; claves no expuestas; conservación/eliminación explícita de clave; protección CSRF; cambio de origen con historial; validaciones del formulario; mantenimiento; datos atrasados; idempotencia de descargas; división de rangos saturados; error y reintento; bloqueo compartido entre visitas; identificación de trabajos por sensor; importación de SQLite en solo lectura; descarte de valores no numéricos; campo de estado configurable; diagnóstico de ceros excluidos del análisis.

## Límites de esta verificación

La consulta al canal real de ThingSpeak no pudo completarse desde el entorno de entrega. Las pruebas de descarga utilizan respuestas simuladas; realiza **Probar conexión** desde tu servidor antes de usar los datos en operación. No se ha desplegado el módulo en tu hosting, cambiado su base de datos ni programado tareas externas.

Las capturas de `dendometro_capturas/` usan lecturas sintéticas para verificar diseño y gráficos. **No son resultados agronómicos reales y no se incorporan a las migraciones ni a la base entregada.**

El sistema conserva las fórmulas del motor de escritorio y documenta las adaptaciones. Esta verificación de software no valida la calibración física del dendrómetro ni demuestra que un umbral diagnostique estrés hídrico.
