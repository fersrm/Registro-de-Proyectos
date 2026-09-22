# Registro de decisiones

## Acuerdos generales de esta base

| ID    | Fecha      | Decisión                                                                                                                                                                                      | Motivo                                                                                                         |
| ----- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| D-001 | 2026-09-20 | Toda necesidad funcional comienza en DOCUMENTAR (`spec → plan → tasks`). Programar requiere una instrucción posterior explícita                                                               | Separar comprensión del negocio de modificaciones y permitir revisión humana                                   |
| D-002 | 2026-09-20 | Las specs `001`–`004` describen código recibido y no representan backlog ni aceptación funcional                                                                                              | Documentación retrospectiva para fijar el punto de partida sin asumir backlog ni compromisos funcionales       |
| D-003 | 2026-09-20 | No ejecutar entrevistas automáticas; reutilizar decisiones escritas y bloquear únicamente las partes afectadas por permisos, exposición pública, datos, dinero, reglas o alcance no definidos | Evitar preguntas sobre puntos resueltos y limitar consultas solo a vacíos críticos                             |
| D-004 | 2026-09-20 | `.env`, base local, claves, medios de usuario y artefactos generados no forman parte de entregas de código/documentación                                                                      | Garantizar la seguridad operativa y prevenir exposición de secretos o datos locales                            |
| D-005 | 2026-09-20 | `django-axes` y correo real no se activan solo por estar instalados o comentados                                                                                                              | Mantener componentes opcionales desactivados hasta contar con spec, configuración, pruebas y plan de reversión |

Estas decisiones expresan el flujo solicitado. Las observaciones técnicas no son decisiones; su priorización y política final se resolverán en futuras specs autorizadas.

## Nueva decisión

Agregar el siguiente ID libre, fecha real, contexto, alternativas relevantes, decisión, quién la confirmó, specs afectadas y consecuencias. Si todavía es propuesta, marcarla como tal. Si reemplaza otra decisión, indicar cuál y conservar la anterior como histórica.

No modificar silenciosamente el requisito para hacerlo coincidir con un bug.
