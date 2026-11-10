# Design

## Context

El código de ventas, el seed, el `Dockerfile`, el `.dockerignore`, `DEPLOY.md` y la evidencia C-01..C-08 ya existen y la suite pasa localmente. Los modelos `Venta`/`RenglonVenta` y la infraestructura (`get_session`, `confirmar`, paginación, health) vienen de C-01..C-03. La máquina del grupo **no tiene Docker** y todavía **no hay acceso al VPS**, así que nada de lo que requiere un contenedor en ejecución puede verificarse ahora. Ver proposal.md para la motivación.

## Goals / Non-Goals

**Goals:**
- Dejar especificado y verificable lo ya construido (ventas, seed, imagen).
- Separar con claridad lo verificable hoy (pytest, revisión estática del `Dockerfile`) de lo pendiente (casos D y despliegue).

**Non-Goals:**
- Cambiar los modelos de ventas (son de `base-y-modelos`).
- Docker Compose o base de datos dentro del contenedor (la consigna lo excluye).
- Envío real de correos: el aviso es simulado.

## Decisions

- **Precios leídos en una sola consulta y libro inexistente detectado antes de escribir.** Se consulta `id, precio` de todos los libros del pedido con `IN`; si falta alguno → 409 con el primer id faltante. Alternativa descartada: dejar que falle la FK del renglón (el mensaje no daría el id concreto, y el precio hay que leerlo igual). El cliente inexistente sí se resuelve por FK (`confirmar` traduce `IntegrityError` a 409), coherente con "no consultar antes si un id existe" del Ejercicio 4.
- **`Decimal` cuantizado a centavos** para subtotal y total; `float` se descarta por errores de redondeo.
- **DTO con `extra="forbid"`**: precio, total o fecha en el cuerpo → 422 automático, sin lógica adicional.
- **Detalle con `joinedload(cliente)` + `selectinload(renglones).joinedload(libro)`**: siempre 2 consultas (C-07). Lazy loading descartado (N+1 y no funciona en async).
- **`BackgroundTasks` + `Depends(get_session, scope="function")`**: la sesión se cierra al terminar el handler y la conexión vuelve al pool antes de que corra el aviso; `asyncio.sleep` (no `time.sleep`) para no bloquear el bucle de eventos.
- **Sin rutas PATCH/DELETE** en ventas: FastAPI responde 405 por sí solo.
- **HEALTHCHECK con `wget` y `127.0.0.1`**: Alpine no trae `curl` y `localhost` resuelve a `::1`, donde uvicorn no escucha.
- **`.dockerignore` ampliado** con `openspec/`, `knowledge-base/`, `CHANGES.md`, `AGENTS.md` y `DEPLOY.md`. Aunque el `Dockerfile` sólo copia `app/` y `requirements.txt`, excluirlos achica el contexto de build y evita que un `COPY . .` futuro los meta. La entrada `*.md` existente sólo cubre la raíz; los nombres explícitos documentan la intención.
- **Casos D modelados como tareas `(PENDIENTE VPS)`**: apply las deja sin marcar con justificación en lugar de fabricar evidencia.

## Risks / Trade-offs

- [El `Dockerfile` nunca se construyó en esta máquina] → revisión estática contra la consigna ahora; D-01/D-02 en el VPS antes de la entrega.
- [La base del VPS puede no estar en `localhost`] → `DEPLOY.md` documenta `host.docker.internal` con `--add-host`.
- [Dependencias que compilen en musl] → ya verificado con `pip download --only-binary` (`evidencia/dependencias_alpine_sin_compilar.txt`).
- [El aviso se pierde si el proceso muere antes de los 0,5 s] → aceptable: es simulado y no transaccional.

## Migration Plan

Despliegue según `DEPLOY.md`: `git clone` en el VPS, `docker build -t libreria .`, `docker run` con `--env-file ~/libreria.env --restart unless-stopped`, `docker exec libreria python -m app.seed`. Actualización: `git pull`, rebuild, `docker rm -f libreria`, mismo `docker run`; los datos viven en la base del servidor. Rollback: reconstruir desde el commit anterior.

## Open Questions

- IP/dominio, puerto asignado y fecha del despliegue: se completan en `DEPLOY.md` el día del despliegue; no cambian specs ni tareas.
