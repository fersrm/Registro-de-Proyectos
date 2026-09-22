# Observaciones contrastadas del proyecto

Estas observaciones provienen del código recibido. No se corrigieron en la fase documental.

| ID | Observación | Riesgo o consecuencia | Próximo tratamiento recomendado |
|---|---|---|---|
| O-001 | `ProyectoDetailView`, `proyecto_qr_view`, `Espacio1View` y QR de espacios no exigen autenticación. | El contenido es público por URL/QR; cambios podrían exponer información adicional. | Confirmar política pública antes de ampliar datos o archivos. |
| O-002 | Crear/editar proyecto guarda el objeto principal antes de validar ambos formsets y retorna dentro de `transaction.atomic()` sin lanzar excepción. | Un formulario secundario inválido puede dejar persistido el objeto principal o cambios parciales. | Spec de corrección con prueba de atomicidad. |
| O-003 | `RecursoProyecto.__str__()` llama `get_tipo_display()`, pero el modelo no tiene campo `tipo`. | Convertir el recurso a texto puede producir `AttributeError` en admin/logs. | Corregir con regresión en spec de proyectos. |
| O-004 | `ProyectoUpdateView` y varias condiciones de plantilla acceden al perfil/cargo de forma distinta al helper central. | Superusuario o usuario sin perfil puede ver navegación distinta o provocar error. | Unificar política y probar matriz completa. |
| O-005 | `templates/pages/index.html` carga `static/js/grafico_home.js`, pero el archivo no está en el ZIP. | Solicitud 404 y gráfico sin comportamiento esperado. | Definir si el gráfico debe recuperarse, reemplazarse o eliminarse. |
| O-006 | Solo Dendrómetro contiene pruebas funcionales; los demás `tests.py` son esqueletos. | Regresiones de usuarios, permisos, proyectos y espacios no están cubiertas. | Incorporar pruebas por módulo al tocar cada flujo. |
| O-007 | Tailwind escanea templates HTML; globs JS/Python están comentados. | Clases construidas exclusivamente en JS/Python pueden ser eliminadas del CSS final. | Activar rutas solo cuando se generen clases allí y verificar el build. |
| O-008 | `.gitignore` ignora globalmente carpetas `migrations/`. | Migraciones nuevas podrían no incluirse en Git. | Revisar política antes de crear la próxima migración. |
| O-009 | `UserListView` requiere login, pero no cargo. | RESTRICTED puede consultar el listado de usuarios según el código actual. | Confirmar si es intencional antes de cambiar. |
| O-010 | Crear proyectos requiere solo autenticación. | Cualquier usuario autenticado puede crear un proyecto. | Mantener como conducta base hasta decisión explícita. |
| O-011 | La suite del dendrómetro no pudo ejecutarse en este entorno por falta de Django. | No hay evidencia nueva de ejecución en esta entrega. | Ejecutar en entorno instalado antes de implementar o liberar. |

No convertir esta tabla en una lista de arreglos automáticos. Cada cambio requiere alcance, aceptación y autorización.
