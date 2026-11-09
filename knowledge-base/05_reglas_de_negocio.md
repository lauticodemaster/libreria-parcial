# Reglas de Negocio

Se conservan los códigos **RN-01 a RN-12 de la consigna** (la corrección los usa); se agrupan por
dominio. Las reglas técnicas transversales llevan el prefijo `RT-`.

## Dominio: Catálogo

- **RN-01**: El ISBN de un libro es único. — Garante: UNIQUE en la base (`uq_libro_isbn`) → 409.
- **RN-03**: El precio de un libro es mayor que cero y el stock nunca es negativo. — Garante: CHECK en la
  base y validación del DTO (422).
- **RN-11**: El listado de libros se puede filtrar por parte del título, sin distinguir mayúsculas. —
  Garante: parámetro ligado, nunca SQL armado con texto (`ILIKE` con `%` y `_` escapados).
- **RT-CAT-01**: El nombre de una editorial y el de un género son únicos (tabla de la consigna) → 409.
- **RT-CAT-02**: El rol de una autoría es autor, coautor, traductor o ilustrador, y el orden es ≥ 1. —
  CHECK en la base y `Literal`/`ge=1` en el DTO.

## Dominio: Clientes

- **RN-02**: El email de un cliente es único. — UNIQUE en la base (`uq_cliente_email`) → 409.
- **RN-09**: Un cliente tiene como máximo un perfil. — UNIQUE en `perfil_cliente.cliente_id` → 409.

## Dominio: Ventas

- **RN-04**: Una venta se crea con sus renglones: los datos de cada renglón viajan dentro del cuerpo del
  alta de la venta y no existe un alta de renglones por separado. — DTO anidado; se agregan a
  `venta.renglones`.
- **RN-05**: Una venta tiene al menos un renglón, y un mismo libro no aparece en dos renglones. —
  Validación del DTO (422).
- **RN-06**: El precio de cada renglón se copia del libro al registrar la venta y no cambia aunque
  después cambie el precio del libro. — El servidor lo lee de la base; nunca viaja en el DTO.
- **RN-07**: El total de la venta lo calcula el servidor como suma de cantidad × precio unitario. — No
  viaja en el DTO.
- **RN-08**: Las ventas no se modifican: registran un hecho. — No hay PATCH (ni DELETE) de ventas.

## Dominio: Excepciones globales

- **RN-10**: Todo listado se pagina con `limit` (de 1 a 100, por defecto 20) y `offset` (desde 0). —
  Restricciones en `Query` → 422.
- **RN-12**: Ningún error devuelve al cliente texto interno de la base (nombres de tablas,
  restricciones o trazas). — Traducción del `IntegrityError` a un mensaje propio.
- **RT-GL-01**: Unicidad, claves foráneas y comprobaciones las garantiza la base; no se verifica antes
  con una consulta. En el alta del libro ningún `if` consulta si un id existe: se escribe y, si la base
  rechaza la clave foránea, se responde 409.
- **RT-GL-02**: Toda relación que se lee se precarga en la misma consulta (`joinedload` a uno,
  `selectinload` colecciones). Prohibida la carga perezosa.
- **RT-GL-03**: El dinero se representa con `Decimal`, nunca con `float`.
- **RT-GL-04**: Todos los handlers son `async def` y ninguno ejecuta una llamada bloqueante.
- **RT-GL-05**: Ninguna contraseña en el código, en el repositorio ni en la imagen.
