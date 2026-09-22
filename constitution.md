# Constitución de desarrollo — Plataforma Agro

Versión 1.0 · 2026-09-20

Estos principios gobiernan el trabajo futuro del proyecto. Las reglas particulares viven en sus specs; una necesidad comercial no modifica esta constitución por sí sola.

1. **Especificar antes de programar.** Todo módulo o cambio funcional empieza por requisitos, plan y tareas. La primera fase es documental; el código requiere una autorización posterior explícita.
2. **Conservar el producto existente.** Antes de editar se inspeccionan el código, los documentos, las specs afectadas y los cambios locales. No se reconstruyen autenticación, tema, navegación ni módulos que ya funcionan.
3. **Una fuente de verdad por regla.** La constitución contiene principios, `AGENTS.md` convenciones técnicas, las specs requisitos verificables y `docs/DECISIONES.md` decisiones transversales. No duplicar reglas incompatibles.
4. **Datos íntegros en servidor.** Permisos, relaciones, unidades, rangos, duplicados y operaciones atómicas se validan en el backend. JavaScript mejora la experiencia, pero no reemplaza la integridad.
5. **Mediciones trazables.** Las lecturas originales del dendrómetro no se alteran para producir gráficos. Conversión, calibración, exclusiones, sesiones, agregaciones y alertas deben ser reproducibles y distinguir datos crudos de resultados derivados.
6. **Integraciones externas controladas.** Las sincronizaciones deben ser idempotentes, reintentables y observables. Un fallo remoto no elimina lecturas válidas ni expone claves de ThingSpeak al cliente.
7. **Acceso mínimo y explícito.** Cada acción define anónimo, usuario activo, RESTRICTED, MANAGER, ADMIN, superusuario y usuario sin perfil cuando aplique. Ocultar un enlace no sustituye autorización en la vista.
8. **Publicación consciente.** Las páginas accesibles por QR pueden ser públicas solo por decisión documentada. Antes de añadir datos personales, archivos o telemetría a ellas se revisan privacidad, enumeración de URL y alcance.
9. **Interfaz para personas.** Español claro, diseño adaptable a móvil, estados comprensibles, errores útiles, navegación por teclado y continuidad con Tailwind y los componentes existentes.
10. **Secretos y datos protegidos.** No incluir `.env`, claves API, bases reales, archivos de usuarios ni información sensible en prompts, pruebas, commits o entregas. Acceder a producción no autoriza modificarla.
11. **Pruebas y evidencia honesta.** Cada cambio relaciona requisito, implementación y comprobación. No declarar ejecutada una prueba que no se ejecutó ni confundir una suite verde con aceptación del usuario, seguridad o capacidad.
12. **Preguntar solo lo crítico.** Reutilizar decisiones documentadas. Preguntar únicamente por vacíos que cambien permisos, exposición pública, datos, dinero, reglas de negocio o alcance; los detalles técnicos reversibles pueden proponerse.
13. **Cambios acotados y recuperables.** No mezclar refactorizaciones, dependencias, despliegues o migraciones ajenas a la tarea. Toda migración explica compatibilidad, respaldo y recuperación.

## Modificación de estos principios

Una modificación requiere motivo, impacto, aprobación explícita, registro en `docs/DECISIONES.md` e incremento de versión. No se cambia la constitución para legitimar una excepción puntual: esa excepción debe quedar en la spec correspondiente.
