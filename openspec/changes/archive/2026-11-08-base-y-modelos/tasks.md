# Tasks

> El código ya existe: cada tarea se verifica contra el archivo y la prueba indicados.

## 1. Estructura y dependencias

- [x] 1.1 Verificar la estructura `app/`, `app/core/`, `app/modules/{health,editoriales,generos,autores,libros,clientes,ventas}/` con `__init__.py`, `tests/` y `test/`, listando los directorios
- [x] 1.2 Verificar `requirements.txt` (versiones fijadas de fastapi[standard], sqlmodel, SQLAlchemy[asyncio], asyncpg, python-dotenv) y `requirements-dev.txt` (`-r requirements.txt` + pytest); verificar que `pip install -r requirements-dev.txt` resuelve
- [x] 1.3 Verificar `pytest.ini` (`testpaths = tests`, `pythonpath = .`) corriendo `pytest --collect-only` sin errores de importación
- [x] 1.4 Verificar `env.example` (forma de `DATABASE_URL`, `SQL_ECHO`, `TEST_DATABASE_URL`, sin secretos) y `.gitignore` (ignora `.env`, `*.env`, `.venv/`, `__pycache__/`, conserva `env.example`)

## 2. Configuración y base de datos

- [x] 2.1 Verificar `app/core/config.py`: `DATABASE_URL` obligatoria sin default y `SQL_ECHO` booleano; pasan `test_sin_database_url_la_configuracion_falla` y `test_sql_echo_se_lee_del_entorno` (4 casos) de `tests/test_health.py`
- [x] 2.2 Verificar `app/core/database.py`: `crear_motor`, `crear_fabrica_de_sesiones` (`expire_on_commit=False`), `crear_tablas` y `get_session`; pasa `test_la_fabrica_de_sesiones_no_expira_al_hacer_commit`

## 3. Utilidades comunes

- [x] 3.1 Verificar `app/core/errores.py`: `nombre_de_restriccion`, `traducir_integridad` (409 por defecto, código por restricción), `confirmar` con rollback y `no_encontrado` (404); se ejercita en `test_c02_isbn_repetido_responde_409_con_mensaje_propio` y `test_c03_segundo_perfil_para_el_mismo_cliente_responde_409`
- [x] 3.2 Verificar `app/core/paginacion.py`: `limit` 1..100 por defecto 20 y `offset` ≥ 0 con 422 fuera de rango; pasan `test_listado_paginado` y `test_paginacion_fuera_de_rango_responde_422` de `tests/test_editoriales.py`

## 4. Aplicación y salud

- [x] 4.1 Verificar `app/main.py`: importa todos los modelos antes de `create_all`; lifespan guarda motor y fábrica en `app.state`, crea tablas y hace `dispose`; pasa `test_el_lifespan_crea_todas_las_tablas_obligatorias`
- [x] 4.2 Verificar en `app/main.py` el manejador global de `IntegrityError` (409 con `MENSAJE_GENERICO`) y `registrar_routers` (omite sólo el `ModuleNotFoundError` de la propia ruta, con aviso en el log)
- [x] 4.3 Verificar `app/modules/health/` (router, service, schemas): `/health/live` y `/health/ready` con 503 si la base cae; pasan `test_live_responde_vivo_sin_tocar_la_base` y `test_ready_ejecuta_select_1_y_responde_listo`
- [x] 4.4 Verificar `test/health.http` con los dos pedidos y la respuesta esperada en comentario

## 5. Modelo de datos

- [x] 5.1 Verificar `editoriales/models.py`, `generos/models.py` y `autores/models.py`: columnas, `uq_editorial_nombre`, `uq_genero_nombre`, relaciones `libros`/`autorias` con `back_populates` y `lazy="raise"`
- [x] 5.2 Verificar `libros/models.py`: `Libro` (Decimal NUMERIC 10,2, `uq_libro_isbn`, `ck_libro_precio_positivo`, `ck_libro_stock_no_negativo`, `editorial_id` indexado, `genero_id` nulo e indexado) y `LibroAutor` (PK compuesta, `autor_id` indexado, `ck_libro_autor_orden`, `ck_libro_autor_rol`, autorías ordenadas por `orden`); se ejercita en `tests/test_libros.py`
- [x] 5.3 Verificar `clientes/models.py`: `uq_cliente_email`, `uq_perfil_cliente_cliente_id`, `Cliente.perfil` con `uselist=False`; pasa `test_detalle_con_perfil_vacio_y_luego_con_perfil` de `tests/test_clientes.py`
- [x] 5.4 Verificar `ventas/models.py`: `fecha` timestamptz, `total` NUMERIC 12,2 con `ck_venta_total_no_negativo`, renglones con `cascade="all, delete-orphan"`, `venta_id` con `ON DELETE CASCADE`, `uq_renglon_venta_venta_libro` y los dos CHECK del renglón; se ejercita en `tests/test_ventas.py`
- [x] 5.5 Verificar que todas las relaciones tienen ambos extremos con `back_populates` y `lazy="raise"`, y que no hay `float` en importes (grep sobre `app/modules/*/models.py`); las pruebas de cantidad fija de consultas (C-07) pasan

## 6. Infraestructura de pruebas e integración

- [x] 6.1 Verificar `tests/conftest.py`: `TEST_DATABASE_URL` → `DATABASE_URL`, salteo si falta, fixtures `aplicacion` (TRUNCATE de las 9 tablas), `cliente`, `insertar` y `contador`; sin la variable, `pytest` reporta todo salteado
- [x] 6.2 Correr la suite completa con `TEST_DATABASE_URL` definida: 83/83 pasan

## Verificación (apply, 09/11/2026)

El código ya existía: cada tarea se verificó contra el archivo indicado y contra las pruebas.
- Suite completa contra PostgreSQL 16.2 (`TEST_DATABASE_URL`): 83 passed.
- Sin `TEST_DATABASE_URL`: todas las pruebas se saltean.
- `test/health.http`, `test/catalogo.http`, `test/libros_clientes.http` y `test/casos_minimos.http` contra
  uvicorn después de `python -m app.seed`: todos los pedidos dan el código esperado.
- 16 relaciones con `back_populates` y `lazy="raise"`; ningún `float` en los modelos.
- No apareció ningún hueco que requiriera código nuevo.
