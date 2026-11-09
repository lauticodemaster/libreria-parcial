# Decisiones y Supuestos

## Decisiones documentadas

### DD-01 — Persona 1 escribe todos los modelos de tabla
**Decisión**: los 7 `models.py` van en el primer commit, junto con la base.
**Contexto**: las relaciones cruzan módulos (`Editorial.libros` → `Libro`, `Cliente.ventas` → `Venta`).
**Alternativas consideradas**: cada integrante sube los modelos de sus módulos.
**Justificación**: con la alternativa, la aplicación no arranca hasta el último commit porque una
relación apunta a una clase que todavía no existe.
**Trade-offs aceptados**: el commit de P1 es más grande; P3 y P4 no escriben sus modelos.

### DD-02 — Registro tolerante de routers en `main.py`
**Decisión**: `main.py` registra los routers de los 7 módulos y omite, con un aviso en el log, los que
todavía no existen.
**Justificación**: `main.py` lo crea P1 completo y nadie más lo toca; cada commit arranca.

### DD-03 — Mensajes de error por nombre de restricción
**Decisión**: cada restricción tiene nombre explícito (`uq_*`, `ck_*`) y cada service mapea nombre →
mensaje; `app/core/errores.py` hace la mecánica común.
**Justificación**: RN-12 sin consultar antes (RT-GL-01).

### DD-04 — `lazy="raise"` en todas las relaciones
**Justificación**: hace imposible depender de la carga perezosa; un olvido de precarga falla en las
pruebas en lugar de pasar inadvertido.

### DD-05 — Precios leídos en una consulta en el alta de venta
**Decisión**: la venta lee `id, precio` de todos sus libros con un `IN (…)` y responde 409 si falta uno.
**Justificación**: RN-06 exige leer el precio de la base; es la única lectura previa permitida.

### DD-06 — Sesión con `scope="function"` en el alta de venta
**Justificación**: la sesión se cierra antes de responder, así la conexión no queda tomada durante el
aviso de 0,5 s.

### DD-07 — `extra="forbid"` en los DTO de alta
**Justificación**: si alguien manda `id`, `precio_unitario`, `total` o `fecha`, recibe 422 en lugar de
que se ignore en silencio (RN-06, RN-07).

### DD-08 — Pruebas contra PostgreSQL real
**Decisión**: pytest + httpx contra una base de prueba (`TEST_DATABASE_URL`), no SQLite.
**Justificación**: los CHECK, los nombres de restricción y asyncpg sólo se prueban de verdad en PostgreSQL.

### DD-09 — Versiones fijadas
`fastapi[standard]==0.162.2`, `sqlmodel==0.0.48`, `SQLAlchemy[asyncio]==2.1.8`, `asyncpg==0.32.0`,
`python-dotenv==1.2.4`. Todas tienen wheel musllinux: la imagen Alpine no necesita compilador.

## Supuestos inferidos

### SU-01 — No se descuenta stock al vender
**Origen**: la consigna no lo pide. **Riesgo si es falso**: el stock no refleja las ventas.
**Cómo validar**: consultar a la cátedra.

### SU-02 — Las columnas listadas son NOT NULL salvo `genero_id`
**Origen**: la consigna sólo marca "nulo permitido" en `genero_id`.

### SU-03 — El perfil de un cliente inexistente responde 404
**Origen**: la tabla de endpoints da 201, 404, 409 para `POST /clientes/{id}/perfil`. Se traduce la
clave foránea rechazada a 404.
