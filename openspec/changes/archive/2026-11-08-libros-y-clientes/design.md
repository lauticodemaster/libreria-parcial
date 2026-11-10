# Design

## Context

Ver proposal.md (Why). Los modelos `Libro`, `LibroAutor`, `Cliente` y `PerfilCliente` ya los dejó el change
`base-y-modelos`, con restricciones con nombre (`uq_libro_isbn`, `uq_cliente_email`,
`uq_perfil_cliente_cliente_id`) y todas las relaciones con `lazy="raise"`. El código de este change ya existe;
el apply verifica cada tarea contra el código y las pruebas.

## Goals / Non-Goals

**Goals:**
- Altas que confían en la base para unicidad y claves foráneas.
- Lecturas con una cantidad fija de consultas.

**Non-Goals:**
- Modificar las autorías de un libro existente (el PATCH no toca `autores`).
- Borrar libros o clientes.

## Decisions

- **Sin consulta previa en el alta de libro**: se arma `Libro` con sus `LibroAutor` y se hace commit; el
  `IntegrityError` se traduce por nombre de restricción (`libro_editorial_id_fkey`, `libro_genero_id_fkey`,
  `libro_autor_autor_id_fkey`, `uq_libro_isbn`). Alternativa descartada: verificar cada id con un SELECT
  (la consigna lo prohíbe y abre una carrera entre la consulta y la escritura).
- **Autor repetido en el DTO (422)**: con dos autorías del mismo autor la base rechazaría la clave primaria,
  pero se valida antes en el DTO para dar un 422 claro. La restricción de la base queda como respaldo (409).
- **Carga anticipada**: listado con `joinedload(editorial, genero)` (1 consulta); detalle con además
  `selectinload(autorias).joinedload(autor)` (2 consultas) y `populate_existing` para releer después del alta.
- **Búsqueda literal**: `ILIKE` con el texto como parámetro ligado y `%`, `_` y `\` escapados (`escape="\\"`),
  así `%` o `_` no traen todo el catálogo.
- **Perfil de cliente inexistente → 404**: la base rechaza `perfil_cliente_cliente_id_fkey` y se traduce a 404
  (la consigna da 201, 404, 409 para ese endpoint), sin consulta previa.
- **Salida armada en el DTO**: `LibroDetalle.desde()` y `ClienteConPerfil.desde()` arman la respuesta a partir
  de objetos ya cargados, sin depender de que FastAPI recorra relaciones.

## Risks / Trade-offs

- El mensaje de un 409 depende del nombre por defecto que PostgreSQL da a las claves foráneas
  (`<tabla>_<columna>_fkey`); si cambia, se cae al mensaje genérico (sigue sin texto interno).
- El listado de ventas del cliente no trae los renglones (sólo id, fecha y total), por diseño.
