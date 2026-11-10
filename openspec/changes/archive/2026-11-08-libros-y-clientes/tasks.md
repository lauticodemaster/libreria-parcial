# Tasks

## 1. Libros: contratos

- [x] 1.1 `app/modules/libros/schemas.py`: `LibroCreate` sin id (`extra="forbid"`), precio `Decimal` > 0, stock ≥ 0, `AutoriaCreate` con rol `Literal` y orden ≥ 1, autores sin repetir; `LibroUpdate` con `genero_id` nulo permitido y el resto no nulo
- [x] 1.2 DTO de salida `LibroListado` (editorial y género) y `LibroDetalle` (más autores con rol y orden)

## 2. Libros: servicio y rutas

- [x] 2.1 `service.crear` sin consulta previa; mensajes propios por restricción (`uq_libro_isbn` y las tres claves foráneas)
- [x] 2.2 `service.listar` con `joinedload`, paginación, filtro por título con parámetro ligado y comodines escapados, filtro por `genero_id`
- [x] 2.3 `service.obtener_detalle` con `joinedload` + `selectinload` (2 consultas fijas) y 404 propio
- [x] 2.4 `service.actualizar` con `exclude_unset` y traducción de errores
- [x] 2.5 `router.py`: POST 201, GET listado, GET detalle, PATCH, con restricciones en `Query`

## 3. Clientes

- [x] 3.1 `app/modules/clientes/schemas.py`: `ClienteCreate` con `EmailStr`, `ClienteUpdate` parcial, `PerfilCreate`, `PerfilRead`, `ClienteConPerfil` (perfil objeto o null), `VentaDelCliente`
- [x] 3.2 `service.py`: alta con `uq_cliente_email` → 409; detalle con `joinedload(perfil)`; PATCH; perfil con `uq_perfil_cliente_cliente_id` → 409 y clave foránea → 404; ventas del cliente paginadas con 404
- [x] 3.3 `router.py`: POST 201, GET, PATCH, POST perfil 201, GET ventas

## 4. Verificación

- [x] 4.1 `tests/test_libros.py` cubre C-01, C-02, C-04, C-07, C-08, contrato 422, paginación y PATCH
- [x] 4.2 `tests/test_clientes.py` cubre C-02 (email), C-03, perfil 404, PATCH y ventas del cliente
- [x] 4.3 `test/libros_clientes.http` tiene la respuesta esperada en un comentario en cada pedido
- [x] 4.4 Correr la suite completa: 83/83

## Verificación (apply, 09/11/2026)

El código ya existía: cada tarea se verificó contra el archivo indicado y contra las pruebas.
- Suite completa contra PostgreSQL 16.2 (`TEST_DATABASE_URL`): 83 passed.
- Sin `TEST_DATABASE_URL`: todas las pruebas se saltean.
- `test/health.http`, `test/catalogo.http`, `test/libros_clientes.http` y `test/casos_minimos.http` contra
  uvicorn después de `python -m app.seed`: todos los pedidos dan el código esperado.
- 16 relaciones con `back_populates` y `lazy="raise"`; ningún `float` en los modelos.
- No apareció ningún hueco que requiriera código nuevo.
