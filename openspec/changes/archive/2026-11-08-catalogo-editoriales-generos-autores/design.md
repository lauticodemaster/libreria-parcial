# Design

## Context

Los modelos de tabla y la infraestructura común (`app/core/errores.py`, `app/core/paginacion.py`, sesión async) los aporta C-01 `base-y-modelos`. Este change agrega la capa de contratos, servicio y router de tres módulos del catálogo. Motivación en proposal.md; requisitos en `specs/catalogo/spec.md`.

## Goals / Non-Goals

**Goals:**
- Contratos HTTP estables e independientes del esquema de tablas.
- Errores con mensaje propio, sin texto de la base (RN-12).

**Non-Goals:**
- Borrado de editoriales, géneros o autores (no lo pide la consigna).
- Alta de libros y autorías (C-03).

## Decisions

- **DTO separados del modelo** (`*Create`, `*Update`, `*Read`, `LibroDe*`): el alta usa `extra="forbid"` y no declara `id`, así un `id` en el cuerpo responde 422. El `Update` tiene todos los campos opcionales, se aplica con `model_dump(exclude_unset=True)` y un validador rechaza `null` explícito. Alternativa descartada: reutilizar el modelo de tabla como cuerpo, que expondría `id` y relaciones.
- **La base garantiza la unicidad**: no se consulta si el nombre existe antes de escribir; se hace commit y `confirmar()` traduce el `IntegrityError` de `uq_editorial_nombre` / `uq_genero_nombre` a 409 con el mensaje del diccionario `MENSAJES` del service. Alternativa descartada: SELECT previo, que deja una carrera entre dos altas concurrentes.
- **404 vía `no_encontrado()`** con el sustantivo del recurso ("La editorial", "El género", "El autor"), para mensajes uniformes.
- **Libros del autor con `joinedload(LibroAutor.libro)`**: se consulta `libro_autor` filtrando por autor y se precarga el libro (relación a uno) en la misma consulta, evitando N+1 y respetando `lazy="raise"` de los modelos. Alternativa descartada: `selectinload`, que suma una consulta y conviene más para colecciones.
- **Paginación común** con `PaginacionDep` (`limit` 1..100, default 20; `offset` desde 0) y orden por id para resultados deterministas.

## Risks / Trade-offs

- [El nombre de la restricción viene del driver] → `nombre_de_restriccion()` lo busca en la excepción original y en su causa; si falta, se usa el mensaje genérico (sigue siendo 409 sin texto interno).
- [Autores sin restricción de unicidad] → `MENSAJES` de autores queda vacío; cualquier rechazo inesperado usa el mensaje genérico.
