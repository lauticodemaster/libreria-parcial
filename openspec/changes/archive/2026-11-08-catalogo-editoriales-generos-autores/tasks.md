# Tasks

## 1. Editoriales

- [x] 1.1 Definir `EditorialCreate` (sin id, `extra="forbid"`), `EditorialUpdate` (opcionales, rechaza `null`), `EditorialRead` y `LibroDeEditorial` en `app/modules/editoriales/schemas.py`; verificar con `test_el_alta_no_acepta_id_ni_campos_vacios` y `test_patch_rechaza_nulos_y_responde_404_si_no_existe`
- [x] 1.2 Implementar `crear`, `listar`, `obtener`, `actualizar` (`exclude_unset`) y `libros_de` en `app/modules/editoriales/service.py`, con la unicidad resuelta por `uq_editorial_nombre` y el mensaje "Ya existe una editorial con ese nombre."; verificar con `test_nombre_repetido_responde_409_con_mensaje_propio` y `test_patch_con_nombre_repetido_responde_409`
- [x] 1.3 Exponer POST/GET `/editoriales/`, GET/PATCH `/editoriales/{id}` y GET `/editoriales/{id}/libros` en `app/modules/editoriales/router.py`; verificar que `pytest tests/test_editoriales.py` pase completo (alta 201, listado paginado, 422 por paginación, detalle 404/422, PATCH parcial, libros 200/404)

## 2. Géneros

- [x] 2.1 Definir `GeneroCreate` (sin id, `extra="forbid"`), `GeneroRead` y `LibroDelGenero` en `app/modules/generos/schemas.py`; verificar con `test_crear_genero_devuelve_201`
- [x] 2.2 Implementar `crear`, `listar` y `libros_de` en `app/modules/generos/service.py` con los mensajes "Ya existe un género con ese nombre." y "El género no existe."; verificar con `test_genero_repetido_responde_409_con_mensaje_propio` y `test_libros_del_genero`
- [x] 2.3 Exponer POST/GET `/generos/` y GET `/generos/{id}/libros` en `app/modules/generos/router.py`; verificar que `pytest tests/test_generos.py` pase completo

## 3. Autores

- [x] 3.1 Definir `AutorCreate`, `AutorUpdate`, `AutorRead` y `LibroDelAutor` (`libro_id`, `isbn`, `titulo`, `rol`, `orden`) en `app/modules/autores/schemas.py`; verificar con `test_alta_de_autor_invalida_responde_422`
- [x] 3.2 Implementar `crear`, `listar`, `obtener`, `actualizar` y `libros_de` (consulta sobre `libro_autor` con `joinedload(LibroAutor.libro)`) en `app/modules/autores/service.py`; verificar con `test_patch_de_autor_es_parcial` y `test_libros_del_autor_con_rol_y_orden`
- [x] 3.3 Exponer POST/GET `/autores/`, GET/PATCH `/autores/{id}` y GET `/autores/{id}/libros` en `app/modules/autores/router.py`; verificar que `pytest tests/test_autores.py` pase completo (incluye `test_autor_inexistente_404_y_no_entero_422`)

## 4. Verificación manual e integración

- [x] 4.1 Recorrer `test/catalogo.http` contra la API levantada tras `python -m app.seed` y verificar que cada respuesta coincida con el "Esperado" de cada caso
- [x] 4.2 Correr la suite completa: 83/83 (`pytest` con todas las pruebas en verde)

## Workflow follow-up

- Archivar el change una vez revisado para desbloquear C-03 `libros-y-clientes`.

## Verificación (apply, 09/11/2026)

El código ya existía: cada tarea se verificó contra el archivo indicado y contra las pruebas.
- Suite completa contra PostgreSQL 16.2 (`TEST_DATABASE_URL`): 83 passed.
- Sin `TEST_DATABASE_URL`: todas las pruebas se saltean.
- `test/health.http`, `test/catalogo.http`, `test/libros_clientes.http` y `test/casos_minimos.http` contra
  uvicorn después de `python -m app.seed`: todos los pedidos dan el código esperado.
- 16 relaciones con `back_populates` y `lazy="raise"`; ningún `float` en los modelos.
- No apareció ningún hueco que requiriera código nuevo.
