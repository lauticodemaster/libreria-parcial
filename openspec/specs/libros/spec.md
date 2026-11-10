# libros Specification

## Purpose
Registrar y consultar los libros del catálogo con su editorial, su género optativo y sus autores (con el rol y
el orden de cada autoría), sin depender de la carga perezosa.

## Requirements

### Requirement: Alta de libro con ids y autorías
El sistema SHALL dar de alta un libro a partir de `isbn`, `titulo`, `precio`, `stock`, `editorial_id`,
`genero_id` (optativo) y la lista `autores`, donde cada elemento trae `autor_id`, `rol` y `orden`, y SHALL
responder 201 con el detalle del libro. El cuerpo MUST NOT llevar `id`.

#### Scenario: Alta válida con dos coautores
- **WHEN** se envía `POST /libros/` con el cuerpo de ejemplo de la consigna (editorial 1, género 1, autores 3 y 4 como coautores con orden 1 y 2)
- **THEN** la respuesta es 201 con la editorial, el género y los autores ordenados por `orden`

#### Scenario: Libro sin género
- **WHEN** se envía el alta con `genero_id` nulo y sin autores
- **THEN** la respuesta es 201 con `genero` en null y `autores` vacío

### Requirement: La base garantiza ISBN único y claves foráneas
El sistema MUST NOT consultar antes si el ISBN o los ids existen: SHALL escribir y, si la base rechaza la
escritura, SHALL responder 409 con un mensaje propio, sin texto interno de la base.

#### Scenario: C-02 ISBN repetido
- **WHEN** se da de alta un libro con un ISBN que ya existe
- **THEN** la respuesta es 409 con `"Ya existe un libro con ese ISBN."`

#### Scenario: C-04 editorial inexistente
- **WHEN** se da de alta un libro con `editorial_id` 999
- **THEN** la respuesta es 409 con `"La editorial indicada no existe."`

#### Scenario: C-04 autor inexistente
- **WHEN** se da de alta un libro con un `autor_id` que no existe
- **THEN** la respuesta es 409 con `"Alguno de los autores indicados no existe."` y el libro no queda registrado

### Requirement: Contrato del alta de libro
El sistema SHALL responder 422 sin ejecutar el alta cuando el cuerpo no cumple el contrato: precio menor o
igual a cero, stock negativo, rol fuera de autor/coautor/traductor/ilustrador, orden menor que 1, un autor
repetido o un campo no previsto.

#### Scenario: Precio cero
- **WHEN** se envía el alta con `precio` "0"
- **THEN** la respuesta es 422

#### Scenario: Rol inválido
- **WHEN** una autoría trae `rol` "editor"
- **THEN** la respuesta es 422

### Requirement: Listado paginado con editorial y género
`GET /libros/` SHALL devolver cada libro con su editorial y su género (o null), paginado con `limit` (1 a 100,
20 por defecto) y `offset` (desde 0), en una sola consulta a la base.

#### Scenario: Paginación
- **WHEN** hay 5 libros y se pide `limit=2&offset=2`
- **THEN** se devuelven los libros 3 y 4

#### Scenario: limit fuera de rango
- **WHEN** se pide `limit=500`
- **THEN** la respuesta es 422

### Requirement: Búsqueda por título con parámetro ligado
El listado SHALL filtrar por parte del título sin distinguir mayúsculas y por `genero_id`. El texto buscado
MUST viajar como parámetro ligado y se busca literalmente (los comodines `%` y `_` no actúan como tales).

#### Scenario: Búsqueda sin distinguir mayúsculas
- **WHEN** se pide `titulo=rAyUeLa`
- **THEN** se devuelven los libros cuyo título contiene "Rayuela"

#### Scenario: C-08 intento de inyección
- **WHEN** se pide `titulo=' OR '1'='1`
- **THEN** la respuesta es 200 con una lista vacía

### Requirement: Detalle de libro sin N+1
`GET /libros/{id}` SHALL devolver el libro con su editorial, su género y sus autores (rol y orden) usando una
cantidad fija de consultas, que no crece con la cantidad de autores.

#### Scenario: C-07 cantidad fija de consultas
- **WHEN** se pide el detalle de un libro con 1 autor y el de uno con 4 autores
- **THEN** ambos pedidos emiten la misma cantidad de consultas (2)

#### Scenario: C-01 id no entero
- **WHEN** se pide `GET /libros/abc`
- **THEN** la respuesta es 422 sin ejecutar el handler

#### Scenario: Libro inexistente
- **WHEN** se pide `GET /libros/99` y no existe
- **THEN** la respuesta es 404 con `"El libro no existe."`

### Requirement: Modificación parcial de libro
`PATCH /libros/{id}` SHALL aplicar sólo los campos enviados y responder con el detalle. `genero_id` MAY ser
null (quita el género); los demás campos MUST NOT ser null.

#### Scenario: Cambio de precio
- **WHEN** se envía `{"precio": "23500.50", "genero_id": null}`
- **THEN** la respuesta es 200 con el precio nuevo, sin género y el resto igual

#### Scenario: Errores del PATCH
- **WHEN** el libro no existe, el ISBN se repite, la editorial no existe o el stock es negativo
- **THEN** las respuestas son 404, 409, 409 y 422 respectivamente
