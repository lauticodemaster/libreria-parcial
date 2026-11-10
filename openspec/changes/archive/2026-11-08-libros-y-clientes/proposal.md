# Proposal

## Why

La librería necesita registrar sus libros con las cosas que ya existen (editorial, género y autores con su
rol y orden) y a sus clientes con un perfil opcional. Es la parte de Persona 3 del reparto y la base de las
ventas del change siguiente. Cubre los ejercicios 3, 4 y 5 de la consigna y los casos C-01 a C-04, C-07 y C-08.

## What Changes

- Alta de libro con `editorial_id`, `genero_id` (optativo) y la lista `autores` (`autor_id`, `rol`, `orden`),
  sin consultar antes si los ids existen: si la base rechaza la clave foránea, 409 con mensaje propio.
- Listado de libros con editorial y género, paginado y filtrable por parte del título (sin distinguir
  mayúsculas, parámetro ligado) y por género.
- Detalle de libro con editorial, género y autores en una cantidad fija de consultas.
- Modificación parcial de libro.
- Alta, detalle con perfil (objeto o null) y modificación parcial de clientes.
- Alta del perfil del cliente (uno a uno) y listado de las ventas del cliente.

## Capabilities

### New Capabilities
- `libros`: alta con autorías, listado y búsqueda, detalle sin N+1 y modificación parcial de libros.
- `clientes`: alta y modificación de clientes, perfil uno a uno y consulta de sus ventas.

### Modified Capabilities

## Impact

- Código: `app/modules/libros/{schemas,service,router}.py`, `app/modules/clientes/{schemas,service,router}.py`.
- Pruebas: `tests/test_libros.py`, `tests/test_clientes.py`; pedidos de ejemplo en `test/libros_clientes.http`.
- Usa los modelos `Libro`, `LibroAutor`, `Cliente` y `PerfilCliente` del change `base-y-modelos` y los
  módulos de catálogo del change `catalogo-editoriales-generos-autores`.
- API: `/libros/` y `/clientes/`. Sin dependencias nuevas.
