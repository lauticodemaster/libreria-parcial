# Proposal

## Why

El parcial de la librería necesita una base común sobre la que los otros tres integrantes construyen sus módulos: conexión asincrónica a PostgreSQL, ciclo de vida de la aplicación, salud del servicio y el modelo de datos completo con sus restricciones (Ejercicios 1 y 2 de la consigna, 30 puntos). Sin esta base ningún commit posterior arranca, porque las relaciones del modelo cruzan módulos.

## What Changes

- Estructura del proyecto: `app/`, `app/core/`, `app/modules/<7 módulos>/`, `tests/`, `test/`, `pytest.ini`, `requirements.txt`, `requirements-dev.txt`, `env.example`, `.gitignore`.
- Configuración: `DATABASE_URL` obligatoria y sin valor por defecto; `SQL_ECHO` opcional para ver las consultas en la consola.
- Motor asincrónico y fábrica de sesiones (`expire_on_commit=False`) creados en el lifespan, guardados en `app.state` y cerrados al apagar; una sesión por petición con `Depends(get_session)`.
- `create_all` al arrancar con todos los modelos importados: crea las tablas que faltan y no altera las existentes.
- Utilidades comunes: traducción de `IntegrityError` a 409 (o 404) con mensaje propio según el nombre de la restricción; paginación común (`limit` 1..100, por defecto 20; `offset` ≥ 0; 422 fuera de rango).
- Manejador global de `IntegrityError` como red de seguridad y registro tolerante de routers.
- Módulo `health`: `GET /health/live` (sin base) y `GET /health/ready` (`SELECT 1`, 503 si la base no responde).
- Los `models.py` de los 7 módulos: las 9 tablas obligatorias con UNIQUE/CHECK nombrados, claves foráneas indexadas, navegación en ambos extremos con `lazy="raise"`, dinero en `Decimal`, fecha con zona horaria, `LibroAutor` como objeto de asociación, `Cliente.perfil` como objeto y composición venta → renglones.
- Infraestructura de pruebas contra PostgreSQL real (`tests/conftest.py`) y pruebas de salud y arranque (`tests/test_health.py`, `test/health.http`).

## Capabilities

### New Capabilities
- `proyecto-base`: configuración por entorno, ciclo de vida (motor, sesiones, creación del esquema), salud del servicio, traducción de errores de integridad y paginación común.
- `modelo-de-datos`: las 9 tablas obligatorias del dominio con sus columnas, tipos, restricciones, índices y navegación entre entidades.

### Modified Capabilities
<!-- Ninguna: no hay specs previas en openspec/specs/. -->

## Impact

- Código: `app/core/*`, `app/main.py`, `app/modules/health/*`, `app/modules/*/models.py`.
- Archivos de proyecto: `requirements.txt`, `requirements-dev.txt`, `env.example`, `.gitignore`, `pytest.ini`.
- Pruebas: `tests/conftest.py`, `tests/test_health.py`, `test/health.http`.
- Dependencias: FastAPI, SQLModel, SQLAlchemy async, asyncpg, python-dotenv (versiones fijadas, DD-09); pytest para pruebas.
- Secretos (sensibilidad ALTA): `DATABASE_URL` y `TEST_DATABASE_URL` nunca se versionan; `env.example` sólo muestra la forma.
- Fuera de alcance: routers/services/schemas de catálogo, libros, clientes y ventas (C-02..C-04), Dockerfile y despliegue (C-04).
- Supuesto: el código ya existe y está probado; el apply verifica cada tarea contra el código existente en lugar de reescribirlo.
