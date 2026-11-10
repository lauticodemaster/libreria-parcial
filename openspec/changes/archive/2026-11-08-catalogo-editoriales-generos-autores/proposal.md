# Proposal

## Why

El Ejercicio 3 de la consigna pide exponer el catálogo base (editoriales, géneros y autores) con contratos propios, códigos de respuesta correctos y mensajes de error sin texto interno de la base. Este change (C-02, Persona 2) documenta esa capacidad sobre los modelos que ya aporta `base-y-modelos` (C-01) y deja desbloqueado C-03 `libros-y-clientes`.

## What Changes

- Endpoints de editoriales: `POST /editoriales/`, `GET /editoriales/`, `GET /editoriales/{id}`, `PATCH /editoriales/{id}` y `GET /editoriales/{id}/libros`.
- Endpoints de géneros: `POST /generos/`, `GET /generos/` y `GET /generos/{id}/libros`.
- Endpoints de autores: `POST /autores/`, `GET /autores/`, `GET /autores/{id}`, `PATCH /autores/{id}` y `GET /autores/{id}/libros` (libros con rol y orden).
- DTO de alta sin `id` y con campos extra prohibidos; `PATCH` parcial que rechaza `null`.
- Nombres de editorial y género únicos, garantizados por la base y traducidos a 409 con mensaje propio (RN-12); 404 con mensaje propio para recursos inexistentes.
- Todos los listados paginados con `limit`/`offset` (RN-10).
- Pruebas automatizadas (`tests/test_editoriales.py`, `tests/test_generos.py`, `tests/test_autores.py`) y casos manuales (`test/catalogo.http`).

## Capabilities

### New Capabilities
- `catalogo`: alta, consulta, modificación parcial y listados de libros asociados de editoriales, géneros y autores.

### Modified Capabilities
<!-- Ninguna: no hay specs principales previas. -->

## Impact

- Código: `app/modules/{editoriales,generos,autores}/{schemas,service,router}.py`.
- Usa sin modificar: modelos de C-01 (`editorial`, `genero`, `autor`, `libro`, `libro_autor`), `app/core/errores.py` y `app/core/paginacion.py`.
- Pruebas: `tests/test_editoriales.py`, `tests/test_generos.py`, `tests/test_autores.py`; manual: `test/catalogo.http`.
- API pública nueva bajo `/editoriales`, `/generos` y `/autores`. Sin dependencias nuevas.
- Supuesto: el código y las pruebas ya existen; el change documenta y verifica el comportamiento observado.
