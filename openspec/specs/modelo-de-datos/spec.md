# modelo-de-datos Specification

## Purpose
Define el esquema relacional obligatorio de la librería: tablas, columnas, tipos, restricciones garantizadas por la base, índices de claves foráneas y la navegación entre entidades en ambos extremos.

## Requirements

### Requirement: Tablas y columnas obligatorias
El esquema SHALL contener las tablas `editorial` (id, nombre, pais), `genero` (id, nombre), `autor` (id, nombre, nacionalidad), `libro` (id, isbn, titulo, precio, stock, editorial_id, genero_id), `libro_autor` (libro_id, autor_id, rol, orden), `cliente` (id, nombre, email), `perfil_cliente` (id, cliente_id, telefono, direccion), `venta` (id, cliente_id, fecha, total) y `renglon_venta` (id, venta_id, libro_id, cantidad, precio_unitario), con esos nombres exactos.

#### Scenario: Esquema creado
- **WHEN** la aplicación arranca contra una base vacía
- **THEN** existen las 9 tablas con todas las columnas indicadas

### Requirement: Columnas no nulas salvo el género
Todas las columnas obligatorias SHALL ser NOT NULL, excepto `libro.genero_id`, que MUST admitir nulo (agregación opcional).

#### Scenario: Libro sin género
- **WHEN** se inserta un libro con `genero_id` nulo y una editorial existente
- **THEN** la base lo acepta

#### Scenario: Libro sin editorial
- **WHEN** se inserta un libro con `editorial_id` nulo
- **THEN** la base lo rechaza

### Requirement: Dinero y fechas con tipos exactos
Los importes SHALL guardarse como NUMERIC (`libro.precio` y `renglon_venta.precio_unitario` 10,2; `venta.total` 12,2) y leerse como decimales exactos, nunca como coma flotante. `venta.fecha` MUST guardarse con zona horaria y tomar el instante actual si no se indica.

#### Scenario: Precio exacto
- **WHEN** se guarda un libro con precio `12.30`
- **THEN** al leerlo el precio es el decimal exacto `12.30`

#### Scenario: Fecha con zona horaria
- **WHEN** se crea una venta sin indicar la fecha
- **THEN** la fecha guardada es el instante actual con zona horaria

### Requirement: Unicidad garantizada por la base
La base SHALL garantizar con restricciones nombradas: `uq_editorial_nombre`, `uq_genero_nombre`, `uq_libro_isbn` (RN-01), `uq_cliente_email` (RN-02), `uq_perfil_cliente_cliente_id` (RN-09) y `uq_renglon_venta_venta_libro` (un libro no aparece dos veces en una venta, RN-05).

#### Scenario: ISBN repetido
- **WHEN** se inserta un segundo libro con un ISBN existente
- **THEN** la base lo rechaza con la restricción `uq_libro_isbn`

#### Scenario: Email repetido
- **WHEN** se inserta un segundo cliente con un email existente
- **THEN** la base lo rechaza con la restricción `uq_cliente_email`

#### Scenario: Segundo perfil
- **WHEN** se inserta un segundo perfil para el mismo cliente
- **THEN** la base lo rechaza con la restricción `uq_perfil_cliente_cliente_id`

### Requirement: Comprobaciones garantizadas por la base
La base SHALL garantizar con CHECK nombrados: `ck_libro_precio_positivo` (precio > 0), `ck_libro_stock_no_negativo` (stock >= 0), `ck_libro_autor_orden` (orden >= 1), `ck_libro_autor_rol` (rol en autor, coautor, traductor, ilustrador), `ck_venta_total_no_negativo` (total >= 0), `ck_renglon_venta_cantidad_positiva` (cantidad > 0) y `ck_renglon_venta_precio_positivo` (precio_unitario > 0).

#### Scenario: Precio no positivo
- **WHEN** se inserta un libro con precio 0
- **THEN** la base lo rechaza con `ck_libro_precio_positivo`

#### Scenario: Rol inválido
- **WHEN** se inserta una autoría con rol `editor`
- **THEN** la base la rechaza con `ck_libro_autor_rol`

#### Scenario: Cantidad no positiva
- **WHEN** se inserta un renglón con cantidad 0
- **THEN** la base lo rechaza con `ck_renglon_venta_cantidad_positiva`

### Requirement: Claves foráneas indexadas
Cada clave foránea SHALL apuntar a la tabla correspondiente y MUST estar cubierta por un índice (propio, o como primera columna de una clave primaria o UNIQUE): `libro.editorial_id`, `libro.genero_id`, `libro_autor.libro_id`, `libro_autor.autor_id`, `perfil_cliente.cliente_id`, `venta.cliente_id`, `renglon_venta.venta_id` y `renglon_venta.libro_id`.

#### Scenario: Referencia inexistente
- **WHEN** se inserta un libro con un `editorial_id` que no existe
- **THEN** la base lo rechaza por clave foránea

#### Scenario: Índices presentes
- **WHEN** se inspecciona el esquema creado
- **THEN** cada clave foránea listada está cubierta por un índice

### Requirement: Autorías como objeto de asociación
La relación libro–autor SHALL modelarse con la entidad `libro_autor`, de clave primaria (`libro_id`, `autor_id`), que guarda el rol y el orden. Desde un libro se MUST llegar a sus autores a través de sus autorías, ordenadas por `orden`, y desde un autor a sus libros a través de las suyas.

#### Scenario: Autor repetido en un libro
- **WHEN** se inserta dos veces la misma pareja (libro, autor)
- **THEN** la base lo rechaza por la clave primaria

#### Scenario: Navegación por autorías
- **WHEN** se lee un libro con sus autorías precargadas
- **THEN** cada autoría expone su autor, su rol y su orden, en orden ascendente

### Requirement: Perfil de cliente uno a uno
Un cliente SHALL tener como máximo un perfil; la clave foránea va en `perfil_cliente.cliente_id`. La navegación del cliente a su perfil MUST devolver un único objeto (o nulo), nunca una lista.

#### Scenario: Cliente sin perfil
- **WHEN** se lee un cliente sin perfil con la relación precargada
- **THEN** su perfil es nulo

#### Scenario: Cliente con perfil
- **WHEN** se lee un cliente con perfil con la relación precargada
- **THEN** su perfil es un objeto con teléfono y dirección

### Requirement: Venta compuesta por renglones
Los renglones SHALL pertenecer a su venta (composición): se guardan junto con ella al agregarlos a la venta, se eliminan si se quitan de ella, y la clave foránea `renglon_venta.venta_id` MUST tener ON DELETE CASCADE. La venta referencia a un cliente existente y cada renglón a un libro existente (asociaciones).

#### Scenario: Alta en cascada
- **WHEN** se guarda una venta nueva con dos renglones agregados a ella
- **THEN** se insertan la venta y los dos renglones

#### Scenario: Borrado de la venta
- **WHEN** se borra una venta en la base
- **THEN** se borran también sus renglones

### Requirement: Navegación en ambos extremos sin carga perezosa
Cada clave foránea SHALL tener navegación declarada en los dos extremos (editorial–libros, genero–libros, libro–autorias, autor–autorias, cliente–perfil, cliente–ventas, venta–renglones, libro–renglones). Acceder a una relación no precargada MUST fallar en lugar de emitir una consulta perezosa.

#### Scenario: Relación no precargada
- **WHEN** se accede a `libro.editorial` de un libro leído sin precargar esa relación
- **THEN** se produce un error en lugar de una consulta adicional

#### Scenario: Relación precargada
- **WHEN** se lee un libro precargando su editorial
- **THEN** `libro.editorial` está disponible sin consultas adicionales
