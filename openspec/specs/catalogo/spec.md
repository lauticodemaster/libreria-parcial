# catalogo Specification

## Purpose
Gestiona el catálogo base de la librería: editoriales, géneros y autores, con altas, consultas, modificaciones parciales y los listados de libros asociados a cada uno.

## Requirements

### Requirement: Alta de editorial
El sistema SHALL crear una editorial con `nombre` (1 a 120 caracteres) y `pais` (1 a 80) mediante `POST /editoriales/`, respondiendo 201 con la editorial creada e incluyendo el `id` asignado por la base. El cuerpo MUST NOT aceptar `id` ni campos adicionales.

#### Scenario: Alta válida
- **WHEN** se envía `POST /editoriales/` con `{"nombre": "Sudamericana", "pais": "Argentina"}`
- **THEN** la respuesta es 201 con `{"id": 1, "nombre": "Sudamericana", "pais": "Argentina"}`

#### Scenario: Cuerpo inválido
- **WHEN** se envía un alta sin `pais`, con `nombre` vacío o con un `id` en el cuerpo
- **THEN** la respuesta es 422

### Requirement: Nombre de editorial único
El sistema SHALL rechazar, tanto en el alta como en la modificación, una editorial cuyo nombre ya exista, respondiendo 409 con el mensaje "Ya existe una editorial con ese nombre." y sin exponer texto interno de la base (RN-12).

#### Scenario: Alta con nombre repetido
- **WHEN** se da de alta una editorial con un nombre ya registrado
- **THEN** la respuesta es 409 con `detail` "Ya existe una editorial con ese nombre." y sin nombres de tablas ni restricciones

#### Scenario: PATCH con nombre repetido
- **WHEN** se modifica una editorial con el nombre de otra existente
- **THEN** la respuesta es 409 con `detail` "Ya existe una editorial con ese nombre."

### Requirement: Listados paginados
Todo listado del catálogo (editoriales, géneros, autores y libros asociados) SHALL paginarse con `limit` entre 1 y 100 (20 por defecto) y `offset` desde 0, ordenado por identificador (RN-10). Valores fuera de rango MUST responder 422.

#### Scenario: Página explícita
- **WHEN** se pide `GET /editoriales/?limit=2&offset=1` con tres editoriales cargadas
- **THEN** la respuesta es 200 con la segunda y la tercera editorial

#### Scenario: Parámetros fuera de rango
- **WHEN** se pide un listado con `limit=0`, `limit=101` u `offset=-1`
- **THEN** la respuesta es 422

### Requirement: Detalle de editorial
El sistema SHALL devolver una editorial por id con `GET /editoriales/{id}` (200). Si no existe, MUST responder 404 con "La editorial no existe."; si el id no es entero, 422.

#### Scenario: Editorial inexistente
- **WHEN** se pide `GET /editoriales/999`
- **THEN** la respuesta es 404 con `detail` "La editorial no existe."

#### Scenario: Id no entero
- **WHEN** se pide `GET /editoriales/uno`
- **THEN** la respuesta es 422

### Requirement: Modificación parcial de editorial
`PATCH /editoriales/{id}` SHALL aplicar sólo los campos enviados y responder 200 con la editorial actualizada. Un campo enviado como `null` MUST responder 422; una editorial inexistente, 404.

#### Scenario: Sólo cambia lo enviado
- **WHEN** se envía `PATCH` con `{"pais": "México"}` a una editorial existente
- **THEN** la respuesta es 200, `pais` cambia y `nombre` conserva su valor

#### Scenario: Nulo o inexistente
- **WHEN** se envía `{"nombre": null}` a una editorial existente, o un PATCH válido a una inexistente
- **THEN** la respuesta es 422 en el primer caso y 404 en el segundo

### Requirement: Libros de una editorial
`GET /editoriales/{id}/libros` SHALL devolver 200 con los libros de esa editorial (`id`, `isbn`, `titulo`, `precio`, `stock`), paginados. Si la editorial no existe MUST responder 404.

#### Scenario: Editorial con libros
- **WHEN** se piden los libros de una editorial que tiene libros
- **THEN** la respuesta es 200 con sólo los libros de esa editorial

#### Scenario: Editorial inexistente
- **WHEN** se piden los libros de una editorial que no existe
- **THEN** la respuesta es 404

### Requirement: Alta y listado de géneros
El sistema SHALL crear un género con `nombre` (1 a 80 caracteres, sin `id` ni campos extra) mediante `POST /generos/` (201) y listarlos con `GET /generos/` (200, paginado). Un nombre repetido MUST responder 409 con "Ya existe un género con ese nombre.".

#### Scenario: Alta válida
- **WHEN** se envía `POST /generos/` con `{"nombre": "Novela"}`
- **THEN** la respuesta es 201 con el género creado y su `id`

#### Scenario: Nombre repetido
- **WHEN** se da de alta un género con un nombre ya registrado
- **THEN** la respuesta es 409 con `detail` "Ya existe un género con ese nombre."

### Requirement: Libros de un género
`GET /generos/{id}/libros` SHALL devolver 200 con los libros del género, paginados. Si el género no existe MUST responder 404 con "El género no existe.".

#### Scenario: Género con libros
- **WHEN** se piden los libros de un género existente
- **THEN** la respuesta es 200 con sólo los libros de ese género

#### Scenario: Género inexistente
- **WHEN** se piden los libros de un género que no existe
- **THEN** la respuesta es 404 con `detail` "El género no existe."

### Requirement: Alta, listado y detalle de autores
El sistema SHALL crear un autor con `nombre` (1 a 120) y `nacionalidad` (1 a 80), sin `id` ni campos extra, mediante `POST /autores/` (201), listarlos paginados con `GET /autores/` y devolver uno con `GET /autores/{id}` (200; 404 con "El autor no existe."; 422 si el id no es entero).

#### Scenario: Alta y lectura
- **WHEN** se crea un autor válido y luego se pide su detalle
- **THEN** el alta responde 201 y el detalle 200 con los mismos datos

#### Scenario: Alta inválida
- **WHEN** se envía un alta de autor con campos faltantes o vacíos
- **THEN** la respuesta es 422

#### Scenario: Autor inexistente o id no entero
- **WHEN** se pide `GET /autores/7` sin autores cargados, o `GET /autores/siete`
- **THEN** la respuesta es 404 en el primer caso y 422 en el segundo

### Requirement: Modificación parcial de autor
`PATCH /autores/{id}` SHALL aplicar sólo los campos enviados y responder 200. Un campo `null` MUST responder 422 y un autor inexistente 404.

#### Scenario: PATCH parcial
- **WHEN** se envía `PATCH` con sólo `nombre` a un autor existente
- **THEN** la respuesta es 200 con el nombre nuevo y la `nacionalidad` sin cambios

#### Scenario: Autor inexistente
- **WHEN** se envía `PATCH /autores/7` sin autores cargados
- **THEN** la respuesta es 404

### Requirement: Libros de un autor con rol y orden
`GET /autores/{id}/libros` SHALL devolver 200 con los libros del autor, cada uno con `libro_id`, `isbn`, `titulo`, `rol` y `orden` de la autoría, paginados y ordenados por libro, con una cantidad de consultas que no crece con los resultados. Si el autor no existe MUST responder 404.

#### Scenario: Autor con autorías
- **WHEN** se piden los libros de un autor que es "autor" (orden 1) de un libro y "coautor" (orden 2) de otro
- **THEN** la respuesta es 200 con ambos libros, cada uno con su `rol` y `orden`

#### Scenario: Autor inexistente
- **WHEN** se piden los libros de un autor que no existe
- **THEN** la respuesta es 404
