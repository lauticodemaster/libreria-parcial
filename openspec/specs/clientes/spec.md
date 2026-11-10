# clientes Specification

## Purpose
Registrar a los clientes de la librería, con un perfil opcional de teléfono y dirección (como máximo uno por
cliente), y consultar las ventas de cada cliente.

## Requirements

### Requirement: Alta de cliente con email único
`POST /clientes/` SHALL dar de alta un cliente con `nombre` y `email` válido y responder 201. La unicidad del
email la garantiza la base: un email repetido MUST responder 409 con mensaje propio.

#### Scenario: Alta válida
- **WHEN** se envía `{"nombre": "Tomás Ríos", "email": "tomas@example.com"}`
- **THEN** la respuesta es 201 con el id, el nombre y el email

#### Scenario: C-02 email repetido
- **WHEN** se da de alta un cliente con un email que ya existe
- **THEN** la respuesta es 409 con `"Ya existe un cliente con ese email."`

#### Scenario: Email inválido
- **WHEN** el email no tiene formato válido
- **THEN** la respuesta es 422

### Requirement: Detalle del cliente con su perfil
`GET /clientes/{id}` SHALL devolver el cliente con su perfil como un objeto, o null si no tiene, nunca como
una lista, leído con carga anticipada.

#### Scenario: Cliente sin perfil
- **WHEN** se pide un cliente que no cargó perfil
- **THEN** la respuesta es 200 con `"perfil": null`

#### Scenario: Cliente inexistente
- **WHEN** se pide `GET /clientes/5` y no existe, o `GET /clientes/cinco`
- **THEN** las respuestas son 404 y 422

### Requirement: Un perfil por cliente
`POST /clientes/{id}/perfil` SHALL crear el perfil (teléfono y dirección) y responder 201. Un cliente tiene como
máximo un perfil: la base lo garantiza y un segundo perfil MUST responder 409. Si el cliente no existe, la
respuesta MUST ser 404.

#### Scenario: Alta del perfil
- **WHEN** se envía el perfil de un cliente sin perfil
- **THEN** la respuesta es 201 y el detalle del cliente lo muestra como objeto

#### Scenario: C-03 segundo perfil
- **WHEN** se envía un perfil para un cliente que ya tiene uno
- **THEN** la respuesta es 409 con `"El cliente ya tiene un perfil cargado."`

#### Scenario: Perfil de cliente inexistente
- **WHEN** se envía un perfil para el cliente 77, que no existe
- **THEN** la respuesta es 404 con `"El cliente no existe."`

### Requirement: Modificación parcial de cliente
`PATCH /clientes/{id}` SHALL aplicar sólo los campos enviados y responder con el cliente y su perfil.

#### Scenario: Errores del PATCH
- **WHEN** se cambia sólo el nombre, se usa el email de otro cliente, un email inválido o un cliente inexistente
- **THEN** las respuestas son 200, 409, 422 y 404 respectivamente

### Requirement: Ventas del cliente
`GET /clientes/{id}/ventas` SHALL listar, paginadas, las ventas del cliente con su id, fecha y total, y SHALL
responder 404 si el cliente no existe.

#### Scenario: Sólo las ventas del cliente
- **WHEN** el cliente 1 tiene las ventas 1 y 3 y el cliente 2 la venta 2
- **THEN** `GET /clientes/1/ventas` devuelve las ventas 1 y 3
