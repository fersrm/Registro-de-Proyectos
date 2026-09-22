# Estado del proyecto

Actualizado: 2026-09-20

## Fase

**DOCUMENTACIÓN SDD DE LÍNEA BASE.** No hay implementación funcional autorizada en esta fase.

## Completado

- Estructura y módulos inspeccionados.
- Constitución, instrucciones de agentes, manual, prompts y plantillas SDD incorporados.
- Specs retrospectivas `001`–`004` creadas a partir del código existente.
- Arquitectura, decisiones, observaciones, roadmap y trazabilidad iniciales documentados.
- Secretos, base local, medios de usuario y artefactos de compilación identificados para excluir de la entrega.

## Validación de esta entrega

- Revisión estática de rutas, modelos, vistas, formularios, servicios, templates y configuración relevante.
- Se identificaron 26 métodos de prueba en `DendometroApp/tests/test_module.py`.
- La ejecución se intentó, pero no comenzó porque el entorno temporal no tenía Django instalado (`ModuleNotFoundError`). No se declara suite aprobada.
- `UsuarioApp/tests.py`, `homeApp/tests.py`, `ProyectosApp/tests.py` y `EspaciosApp/tests.py` no contienen casos funcionales.

## Pendientes de decisión, no autorizados

Ver `docs/OBSERVACIONES_PROYECTO.md`. En especial: política pública de páginas QR, atomicidad de formularios de proyectos, consistencia de permisos/superusuario, `__str__` de recursos y referencia a un JS ausente en inicio.

## Siguiente paso

El propietario revisa esta documentación. Para el próximo cambio, inicia en fase DOCUMENTAR con `prompts/00-orquestador.md`; si acepta una spec, autoriza después sus tareas para pasar a implementación.

## Punto de reanudación

No hay spec de cambio activa. El siguiente número libre observado es `005`.
