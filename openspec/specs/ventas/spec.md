# ventas Specification

## Purpose
Registrar ventas de libros a clientes con sus renglones, donde el servidor fija precios y total, y las ventas quedan como hechos inmutables consultables de forma eficiente.

## Requirements

### Requirement: Alta de venta con renglones
El sistema SHALL aceptar `POST /ventas/` con `cliente_id` y una lista `renglones` de objetos `{libro_id, cantidad}`, crear la venta junto con todos sus renglones en una única operación y responder 201 con la venta creada (id, fecha, total, cliente y renglones con `libro_id`, `titulo`, `cantidad`, `precio_unitario` y `subtotal`).

#### Scenario: Venta válida con dos renglones (C-06)
- **WHEN** con los datos iniciales se envía `{"cliente_id": 2, "renglones": [{"libro_id": 1, "cantidad": 2}, {"libro_id": 4, "cantidad": 1}]}`
- **THEN** la respuesta es 201, cada renglón trae el precio copiado del libro y su subtotal, y el `total` es `77000.00`

### Requirement: Precio y total los fija el servidor
El sistema MUST copiar el precio vigente de cada libro como `precio_unitario` del renglón y MUST calcular `subtotal = cantidad × precio_unitario` y `total = Σ subtotales` con aritmética decimal exacta redondeada a centavos. El cuerpo del pedido MUST NOT incluir `precio_unitario`, `total` ni `fecha`.

#### Scenario: El cuerpo trae precio, total o fecha
- **WHEN** el cuerpo de `POST /ventas/` incluye `total`, `fecha` o `precio_unitario` en un renglón
- **THEN** la respuesta es 422 y no se registra ninguna venta

#### Scenario: El total es la suma exacta de los subtotales
- **WHEN** se registra una venta válida
- **THEN** el `total` devuelto es igual a la suma de `cantidad × precio_unitario` de sus renglones, sin errores de redondeo binario

### Requirement: Validación del contrato de alta
El sistema SHALL responder 422 cuando la venta no tiene renglones, cuando un mismo `libro_id` aparece en dos renglones o cuando alguna `cantidad` es menor o igual a cero.

#### Scenario: Venta sin renglones
- **WHEN** se envía `renglones: []`
- **THEN** la respuesta es 422

#### Scenario: Libro repetido
- **WHEN** dos renglones tienen el mismo `libro_id`
- **THEN** la respuesta es 422

#### Scenario: Cantidad no positiva
- **WHEN** un renglón tiene `cantidad` 0 o negativa
- **THEN** la respuesta es 422

### Requirement: Referencias inexistentes responden 409
El sistema SHALL responder 409 cuando algún libro o el cliente de la venta no existen, sin registrar nada. Para un libro inexistente el mensaje MUST ser `"No existe el libro con id N."`; el cliente inexistente se detecta por el rechazo de la clave foránea en la base.

#### Scenario: Libro inexistente (C-05)
- **WHEN** un renglón referencia `libro_id` 9999 que no existe
- **THEN** la respuesta es 409 con el detalle `"No existe el libro con id 9999."`

#### Scenario: Cliente inexistente (C-05)
- **WHEN** `cliente_id` no corresponde a ningún cliente
- **THEN** la respuesta es 409 y no se crea la venta

### Requirement: Las ventas son inmutables
El precio guardado en un renglón MUST NOT cambiar cuando cambia el precio del libro (RN-06). El sistema MUST NOT exponer modificación ni borrado de ventas (RN-08).

#### Scenario: Cambia el precio del libro después de la venta
- **WHEN** después de registrar una venta se modifica el precio de uno de sus libros
- **THEN** `GET /ventas/{id}` sigue mostrando el `precio_unitario` y el `total` originales

#### Scenario: Intento de modificar o borrar una venta
- **WHEN** se envía `PATCH` o `DELETE` a `/ventas/{id}`
- **THEN** la respuesta es 405

### Requirement: Consulta de ventas
El sistema SHALL ofrecer `GET /ventas/` paginado con `limit` y `offset`, y `GET /ventas/{id}` con cliente y renglones. El detalle MUST resolverse con una cantidad fija de consultas a la base, independiente de la cantidad de renglones (C-07). Una venta inexistente responde 404 y un id no entero responde 422.

#### Scenario: Detalle con cantidad fija de consultas (C-07)
- **WHEN** se pide el detalle de una venta con uno o con varios renglones
- **THEN** la base recibe la misma cantidad de consultas (2) en ambos casos

#### Scenario: Listado paginado
- **WHEN** se pide `GET /ventas/?limit=1&offset=1` habiendo dos ventas
- **THEN** la respuesta contiene sólo la segunda venta

#### Scenario: Venta inexistente
- **WHEN** se pide `GET /ventas/9999`
- **THEN** la respuesta es 404

### Requirement: Aviso del comprobante en segundo plano
Tras registrar una venta, el sistema SHALL agendar un aviso del comprobante al cliente que corre después de enviar la respuesta, espera de forma asíncrona (0,5 s simulados) y deja una línea en el registro. El aviso MUST NOT demorar la respuesta ni bloquear la atención de otras peticiones, y la conexión a la base MUST liberarse antes de que corra.

#### Scenario: La respuesta no espera al aviso
- **WHEN** se registra una venta
- **THEN** la respuesta 201 llega antes de que se escriba el log del comprobante, y el log aparece después de la línea `POST /ventas/ ... 201`

#### Scenario: El servidor sigue atendiendo mientras corre el aviso
- **WHEN** un aviso está esperando
- **THEN** otra petición concurrente se responde sin esperar a que el aviso termine

### Requirement: Datos iniciales
El sistema SHALL proveer el comando `python -m app.seed` que vacía las tablas reiniciando los identificadores y carga un conjunto conocido de datos con el que funcionan los ejemplos de la consigna.

#### Scenario: Estado conocido
- **WHEN** se ejecuta el comando de datos iniciales
- **THEN** la base queda con los mismos registros e ids cada vez, y la venta del caso C-06 da total `77000.00`
