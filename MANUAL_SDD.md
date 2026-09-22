# Manual SDD para continuar la Plataforma Agro con Codex

## 1. Flujo recomendado

Cuando pidan un módulo o cambio, indica su nombre y explica el requerimiento en lenguaje natural. No necesitas convertirlo a requisitos técnicos.

```text
Nombre del módulo o cambio: <nombre claro>

Requerimiento:
<qué necesita, quién lo usa, flujo, datos, permisos, validaciones,
ejemplos, exclusiones y qué comportamiento actual debe conservarse>

Fase: DOCUMENTAR, sin código.

Lee AGENTS.md y prompts/00-orquestador.md. Inspecciona el código y la
spec afectada. Genera o actualiza spec.md, después plan.md y finalmente
tasks.md. Actualiza solo los docs necesarios. Pregunta únicamente por
decisiones críticas ausentes. Detente antes de implementar.
```

Para requisitos amplios usa preferentemente un modelo con razonamiento avanzado. El modelo no sustituye la separación de fases ni autoriza trabajo por sí mismo.

## 2. ¿Debo enviar los prompts uno por uno?

No. Normalmente basta con el coordinador `prompts/00-orquestador.md`; Codex seleccionará las guías necesarias y explicará cuáles aplica.

| Caso | Guías | Resultado |
|---|---|---|
| Módulo nuevo | 01 → 02 → 03 | Nueva carpeta numerada con spec, plan y tareas |
| Cambio o error | 06 y luego las documentales necesarias | Actualización de la spec existente o nueva spec transversal |
| Implementación aprobada | 04 | Código para tareas autorizadas |
| Validación | 05 | Evidencia y trazabilidad |
| Pausar/retomar | 07 | Estado recuperable entre sesiones |

Seleccionar una guía no autoriza la fase siguiente. La primera respuesta a una necesidad funcional debe terminar en documentos.

## 3. Línea base y numeración

Este proyecto ya contiene cuatro specs retrospectivas:

- `001-plataforma-y-usuarios`
- `002-proyectos`
- `003-espacios`
- `004-dendrometros`

Describen lo que existe; no son tareas pendientes. Para un módulo distinto se usa el siguiente número libre, actualmente `005`, comprobándolo antes. Un cambio pequeño sobre proyectos, espacios, usuarios o dendrómetros se registra en su spec vigente con requisitos/tareas fechados. Una ampliación transversal puede justificar una spec nueva.

## 4. Revisar y autorizar implementación

Revisa primero requisitos y criterios de aceptación, luego el plan y las tareas. Para corregir documentación:

```text
Revisa la spec <NNN>: <corrección>.
Actualiza spec, plan, tareas y docs afectados.
Seguimos en DOCUMENTAR; no implementes todavía.
```

Cuando estés conforme:

```text
Revisé y apruebo spec.md, plan.md y tasks.md de specs/<carpeta>.
Autorizo implementar <todo el alcance | IDs de tareas>.
Usa prompts/04-implementar.md, conserva mis cambios locales y no amplíes
el alcance. Ejecuta comprobaciones pertinentes y actualiza tareas,
validación, trazabilidad y estado. No despliegues ni uses datos reales.
```

No hace falta autorizar cada archivo dentro de tareas ya aprobadas. Sí hace falta detenerse ante una decisión nueva que cambie acceso público, permisos, datos, integraciones, dinero o alcance.

## 5. Cambios comunes

| Solicitud | Tratamiento |
|---|---|
| Campo/filtro pequeño | Actualizar spec vigente y crear tareas del cambio |
| Módulo distinto | Nueva carpeta numerada |
| Error contra un requisito | Reproducir, documentar regresión y corregir tras autorización |
| Cambio de acceso QR/público | Decisión explícita y matriz de permisos |
| Cambio de cálculo del dendrómetro | Ejemplos numéricos, unidades y regresiones |
| Activar correo o django-axes | Spec/configuración propia con operación y rollback |
| Despliegue | Autorización separada y checklist de producción |

## 6. Validar sin exagerar

Después del código, pide `prompts/05-validar.md`. La entrega debe relacionar RF con prueba, registrar comandos exactos y decir qué no se verificó. En este proyecto el dendrómetro trae 26 casos automatizados; otros módulos aún no tienen cobertura real. Un conteo histórico no reemplaza una ejecución nueva.

Prueba permisos en el servidor y no solo el menú. Para cambios visuales, revisa escritorio y móvil. Para sincronización externa, usa dobles/mocks por defecto; una prueba contra ThingSpeak real requiere autorización y una clave segura.

## 7. Pausar y continuar

Antes de cerrar una sesión:

```text
Usa prompts/07-retomar-pausar.md en modo PAUSAR.
Guarda fase, tareas, archivos, pruebas, bloqueos y siguiente acción.
```

Para continuar:

```text
Modo RETOMAR. Lee AGENTS.md, docs/ESTADO_PROYECTO.md y la spec activa.
Comprueba el código y continúa solo la fase y tareas ya autorizadas.
```

Así no necesitas repetir el requerimiento original ni depender del historial del chat.

## 8. Regla breve

**Requerimiento → spec → plan → tareas → revisión → autorización → código → validación → estado.**

SDD organiza acuerdos y evidencia; no reemplaza Git, respaldos, revisión del usuario ni operación segura.
