# Design

## Context

Ver proposal.md (Why). El equipo son 4 personas con commits secuenciales (C-01 → C-04); cada commit debe dejar una aplicación que arranca. El código de este change ya existe y está probado: el apply verifica cada tarea contra el código y las pruebas existentes. Stack fijado (DD-09): FastAPI, SQLModel, SQLAlchemy 2 async, asyncpg, PostgreSQL 16, Python 3.12. El esquema se crea con `create_all` (sin migraciones, por consigna).

## Goals / Non-Goals

**Goals:**
- Que P2, P3 y P4 sólo agreguen `schemas.py`, `service.py` y `router.py` sin tocar `app/core/`, `app/main.py` ni los modelos.
- Que las garantías de datos (unicidad, CHECK, FK) las dé la base y los errores lleguen al cliente con mensaje propio.
- Que una lectura que olvide precargar una relación falle en las pruebas.

**Non-Goals:**
- Endpoints de catálogo, libros, clientes y ventas (C-02..C-04).
- Dockerfile, despliegue y datos iniciales (`app/seed.py`, C-04).
- Migraciones, autenticación.

## Decisions

### D1 — P1 escribe todos los `models.py` (DD-01)
Las relaciones cruzan módulos (`Editorial.libros` → `Libro`, `Cliente.ventas` → `Venta`). Si cada integrante subiera sus modelos, el mapeo de SQLAlchemy fallaría al arrancar hasta el último commit. Alternativa descartada: modelos por integrante. Costo: commit de P1 más grande.

### D2 — Registro tolerante de routers (DD-02)
`main.py` recorre la tupla fija de 7 módulos e importa `app.modules.<m>.router`; si el `ModuleNotFoundError` corresponde exactamente a esa ruta, lo omite con un aviso; cualquier otro error de importación se propaga para no ocultar fallas reales. Alternativa descartada: que cada integrante edite `main.py` (conflictos y commits que no arrancan).

### D3 — Restricciones con nombre para traducir errores (DD-03)
Cada UNIQUE/CHECK tiene nombre explícito (`uq_*`, `ck_*`). `app/core/errores.py` extrae `constraint_name` de la excepción de asyncpg (en `orig` o su `__cause__`) y cada service declara el diccionario nombre → mensaje (y código opcional, p. ej. 404 para FK). Un manejador global de `IntegrityError` responde 409 genérico como red de seguridad. Alternativa descartada: consultar antes de escribir (prohibido por consigna: carrera y consulta extra).

### D4 — `lazy="raise"` en todas las relaciones (DD-04)
Convierte la carga perezosa (que en async además falla con un error opaco) en un error inmediato y explícito; obliga a `selectinload`/`joinedload` y evita N+1. Alternativa descartada: `lazy="select"` por defecto.

### D5 — Motor y fábrica en el lifespan
Se crean en el lifespan, se guardan en `app.state` y `get_session` toma la fábrica de `request.app.state`. Permite que las pruebas usen la misma app con `TEST_DATABASE_URL`. `expire_on_commit=False` evita recargas implícitas tras el commit. `pool_pre_ping=True` para tolerar conexiones caídas.

### D6 — Configuración sin valor por defecto
`leer_configuracion()` carga `.env` sin pisar el entorno y lanza `RuntimeError` si falta `DATABASE_URL`, cortando el arranque. Evita conectarse por error a una base implícita y cualquier secreto en el código.

### D7 — Detalles del modelo
- Índices de FK: los que ya quedan cubiertos por la primera columna de una PK/UNIQUE (`libro_autor.libro_id`, `perfil_cliente.cliente_id`, `renglon_venta.venta_id`) no llevan índice extra; el resto usa `index=True`.
- `LibroAutor` es clase propia (no `link_model`) porque tiene rol y orden; `Libro.autorias` ordena por `orden` con `cascade="all, delete-orphan"`.
- `Cliente.perfil` con `uselist=False`; el UNIQUE de `cliente_id` hace cumplir el uno a uno.
- `Venta.renglones` con `cascade="all, delete-orphan"` y `renglon_venta.venta_id` con `ON DELETE CASCADE`.
- `venta.fecha` con `DateTime(timezone=True)`, `server_default=now()` y valor por defecto en Python (UTC).

### D8 — Pruebas contra PostgreSQL real (DD-08)
`conftest.py` redirige `DATABASE_URL` a `TEST_DATABASE_URL`, corre el lifespan real, hace `TRUNCATE ... RESTART IDENTITY CASCADE` antes de cada prueba y saltea todo si la variable falta. Incluye un contador de consultas para verificar `SELECT 1` y la ausencia de N+1.

## Risks / Trade-offs

- [`create_all` no altera tablas existentes: un cambio de modelo no llega a una base ya creada] → documentado; para corregir, borrar las tablas de la base de trabajo o de prueba.
- [El registro tolerante podría ocultar un router faltante en la entrega final] → aviso en el log y pruebas de cada módulo que fallan si su router no está.
- [Las pruebas vacían tablas] → sólo usan `TEST_DATABASE_URL`, nunca `DATABASE_URL`; se saltean si falta.
- [Restricción sin mensaje declarado] → mensaje genérico propio, nunca el texto de la base.

## Supuestos

- SU-02: todas las columnas listadas son NOT NULL salvo `genero_id`.
- Las longitudes máximas de texto (`max_length`) son elección del equipo; la consigna no las fija.
- La suite completa (83 casos con parametrizaciones) incluye pruebas de C-02..C-04; para este change se verifica que siga pasando entera.
