# Modelo de Datos

Los **nombres de tablas y columnas son obligatorios** (los usan los casos de prueba y la corrección).
Se pueden agregar columnas, pero no quitar ni renombrar las indicadas.

## Dominios

- **Catálogo**: editorial, genero, autor, libro, libro_autor.
- **Clientes**: cliente, perfil_cliente.
- **Ventas**: venta, renglon_venta.

## ERD

```
editorial 1 ──◇ * libro * ◇── 0..1 genero          (agregación; género opcional)
                   │ 1
                   │
                   * libro_autor * ── 1 autor       (muchos a muchos con datos: rol, orden)
                   │
libro 1 ──── * renglon_venta * ◆── 1 venta          (renglón → libro: asociación;
                                    │ *               venta ◆ renglón: composición)
                                    │
                                    1 cliente 1 ── 0..1 perfil_cliente   (uno a uno)
                                     (venta → cliente: asociación)
```

## Entidades

### editorial — `app/modules/editoriales/models.py`
- `id` serial PK, `nombre` varchar(120) NOT NULL, `pais` varchar(80) NOT NULL.
- `uq_editorial_nombre` UNIQUE (nombre).
- Relación: `Editorial.libros` ↔ `Libro.editorial`.

### genero — `app/modules/generos/models.py`
- `id`, `nombre` varchar(80). `uq_genero_nombre` UNIQUE (nombre).
- Relación: `Genero.libros` ↔ `Libro.genero`.

### autor — `app/modules/autores/models.py`
- `id`, `nombre` varchar(120), `nacionalidad` varchar(80). Sin restricciones extra.
- Relación: `Autor.autorias` ↔ `LibroAutor.autor`.

### libro — `app/modules/libros/models.py`
- `id`, `isbn` varchar(20), `titulo` varchar(200), `precio` NUMERIC(10,2) (`Decimal`), `stock` int,
  `editorial_id` FK NOT NULL, `genero_id` FK **nulo permitido**.
- `uq_libro_isbn` UNIQUE; `ck_libro_precio_positivo` CHECK (precio > 0);
  `ck_libro_stock_no_negativo` CHECK (stock >= 0).
- Índices: `ix_libro_editorial_id`, `ix_libro_genero_id`.
- Relaciones: `editorial`, `genero`, `autorias` (cascade all, delete-orphan; ordenadas por `orden`),
  `renglones`.

### libro_autor — objeto de asociación (`LibroAutor`, en `libros`)
- `libro_id` FK, `autor_id` FK, `rol` varchar(20), `orden` int.
- PK compuesta (libro_id, autor_id) → indexa `libro_id`; `ix_libro_autor_autor_id`.
- `ck_libro_autor_orden` CHECK (orden >= 1);
  `ck_libro_autor_rol` CHECK (rol IN ('autor','coautor','traductor','ilustrador')).
- Se navega `libro.autorias[i].autor`. No se usa `link_model` porque escondería rol y orden.

### cliente — `app/modules/clientes/models.py`
- `id`, `nombre` varchar(120), `email` varchar(200). `uq_cliente_email` UNIQUE.
- Relaciones: `perfil` (objeto, `uselist=False`), `ventas`.

### perfil_cliente — `PerfilCliente`, en `clientes`
- `id`, `cliente_id` FK, `telefono` varchar(40), `direccion` varchar(200).
- `uq_perfil_cliente_cliente_id` UNIQUE (cliente_id): uno a uno, y además indexa la FK.

### venta — `app/modules/ventas/models.py`
- `id`, `cliente_id` FK (`ix_venta_cliente_id`), `fecha` timestamptz (default now()),
  `total` NUMERIC(12,2). `ck_venta_total_no_negativo` CHECK (total >= 0).
- Relaciones: `cliente`, `renglones` (cascade all, delete-orphan).

### renglon_venta — `RenglonVenta`, en `ventas`
- `id`, `venta_id` FK ON DELETE CASCADE, `libro_id` FK (`ix_renglon_venta_libro_id`), `cantidad` int,
  `precio_unitario` NUMERIC(10,2).
- `ck_renglon_venta_cantidad_positiva` CHECK (cantidad > 0);
  `ck_renglon_venta_precio_positivo` CHECK (precio_unitario > 0);
  `uq_renglon_venta_venta_libro` UNIQUE (venta_id, libro_id) → indexa `venta_id`.

Todas las relaciones se declaran en los dos extremos con `back_populates` y `lazy="raise"`.

## Seed data inicial (`python -m app.seed`)

Vacía las tablas (`TRUNCATE … RESTART IDENTITY CASCADE`) y carga:

| Tabla | Filas |
|---|---|
| editorial | 1 Sudamericana, 2 Emecé, 3 Anagrama |
| genero | 1 Novela, 2 Cuento, 3 Ensayo |
| autor | 1 Cortázar, 2 Piglia, 3 Bioy Casares, 4 Ocampo, 5 Borges |
| libro | 1 Rayuela ($25000), 2 Bestiario, 3 La invención de Morel, 4 Respiración artificial ($27000), 5 Ficciones, 6 Antología de la literatura fantástica (sin género, 3 coautores) |
| cliente | 1 Ana Pérez (con perfil), 2 Tomás Ríos (sin perfil), 3 Lucía Gómez |
| venta | 1 venta de Ana (libro 3), para que la venta del ejemplo de la consigna salga con id 2 |
