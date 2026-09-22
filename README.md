# Plataforma Agro

Proyecto Django para gestión de usuarios, proyectos, espacios agroeducativos y monitoreo de dendrómetros. Esta copia incorpora una metodología SDD para continuar su evolución con Codex sin perder alcance, decisiones ni evidencia.

## Inicio rápido de desarrollo

1. Crea y activa un entorno virtual.
2. Instala `requirements.txt`.
3. Crea tu `.env` local con los valores requeridos por `core/settings.py`.
4. Ejecuta migraciones en una base local.
5. Compila Tailwind desde `theme/static_src/` cuando cambien estilos.
6. Inicia Django con `python manage.py runserver`.

No se distribuyen `.env`, bases locales ni archivos cargados por usuarios.

## Trabajar con SDD

- Lee [MANUAL_SDD.md](MANUAL_SDD.md).
- Inicia solicitudes con [prompts/00-orquestador.md](prompts/00-orquestador.md).
- Consulta el catálogo en [specs/README.md](specs/README.md).
- La situación actual está en [docs/ESTADO_PROYECTO.md](docs/ESTADO_PROYECTO.md).

Regla principal: primero documentación (`spec → plan → tasks`), luego revisión humana y después una autorización explícita para implementar.

## Documentación existente

La documentación especializada del dendrómetro se conserva en `LEEME_DENDOMETRO.md` y `docs/DENDOMETRO_*.md`. Los documentos SDD no la reemplazan: la indexan y registran el estado global del producto.
