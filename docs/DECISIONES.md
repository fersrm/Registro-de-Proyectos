# Registro de decisiones

## Acuerdos generales de esta base

| ID    | Fecha      | Decisión                                                                                                                                                                                      | Motivo                                                                                                         |
| ----- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| D-001 | 2026-09-20 | Toda necesidad funcional comienza en DOCUMENTAR (`spec → plan → tasks`). Programar requiere una instrucción posterior explícita                                                               | Separar comprensión del negocio de modificaciones y permitir revisión humana                                   |
| D-002 | 2026-09-20 | Las specs `001`–`004` describen código recibido y no representan backlog ni aceptación funcional                                                                                              | Documentación retrospectiva para fijar el punto de partida sin asumir backlog ni compromisos funcionales       |
| D-003 | 2026-09-20 | No ejecutar entrevistas automáticas; reutilizar decisiones escritas y bloquear únicamente las partes afectadas por permisos, exposición pública, datos, dinero, reglas o alcance no definidos | Evitar preguntas sobre puntos resueltos y limitar consultas solo a vacíos críticos                             |
| D-004 | 2026-09-20 | `.env`, base local, claves, medios de usuario y artefactos generados no forman parte de entregas de código/documentación                                                                      | Garantizar la seguridad operativa y prevenir exposición de secretos o datos locales                            |
| D-005 | 2026-09-20 | `django-axes` y correo real no se activan solo por estar instalados o comentados                                                                                                              | Mantener componentes opcionales desactivados hasta contar con spec, configuración, pruebas y plan de reversión |
| D-006 | 2026-09-22 | El detalle y QR de proyectos, y la ficha y QR de espacios, permanecen públicos sin cuenta; los listados conservan su acceso actual | El propietario confirmó O-001 para consulta pública detallada. Hacer pública la lista de espacios no se incluyó en la observación ni en el alcance confirmado |
| D-007 | 2026-09-22 | El listado de usuarios está disponible para cualquier usuario autenticado, pero no para anónimos; las acciones administrativas siguen limitadas por cargo o superusuario | El propietario confirmó O-009 y la conducta base distingue consulta autenticada de administración |
| D-008 | 2026-09-22 | Cualquier usuario autenticado puede crear proyectos; crear, modificar y eliminar debe dejar un evento de auditoría persistente con actor, fecha e identidad mínima del proyecto | El propietario confirmó O-010 y pidió trazabilidad de quienes agregan, modifican o eliminan |
| D-009 | 2026-09-22 | La compilación de estilos del proyecto se valida con `py manage.py tailwind build`; las fuentes dinámicas reales de JS/Python se agregan mediante globs específicos | Evitar perder clases de `static/js/mensajes.js` y `UsuarioApp/forms.py` sin escanear dependencias o entornos completos |
| D-010 | 2026-09-22 | El cierre de sesión desde la interfaz se ejecuta directamente por `POST` protegido con CSRF; no se habilita el logout por `GET` | Eliminar la confirmación intermedia sin permitir que un enlace externo cierre una sesión del usuario |

Las decisiones D-006 a D-009 fueron implementadas y validadas en la spec 005 el 2026-09-22. La aceptación final del propietario permanece pendiente.

## Nueva decisión

Agregar el siguiente ID libre, fecha real, contexto, alternativas relevantes, decisión, quién la confirmó, specs afectadas y consecuencias. Si todavía es propuesta, marcarla como tal. Si reemplaza otra decisión, indicar cuál y conservar la anterior como histórica.

No modificar silenciosamente el requisito para hacerlo coincidir con un bug.
