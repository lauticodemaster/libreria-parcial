# Descripción General

## Stack tecnológico

| Capa | Tecnología | Versión mínima (consigna) | Versión fijada |
|---|---|---|---|
| Lenguaje | Python | 3.12 | 3.12 |
| Framework web | FastAPI (`fastapi[standard]`), todos los handlers `async def` | 0.111 | 0.162.2 |
| Modelos y contratos | SQLModel | 0.0.24 | 0.0.48 |
| ORM, motor y sesión | SQLAlchemy 2 asincrónico (`SQLAlchemy[asyncio]`) | 2.0 | 2.1.8 |
| Controlador de base | asyncpg | 0.30 | 0.32.0 |
| Base de datos | PostgreSQL (en el VPS, la del servidor) | 16 | 16 |
| Configuración | python-dotenv | 1.0 | 1.2.4 |
| Servidor ASGI | uvicorn (lo instala `fastapi[standard]`) | — | 0.54 |
| Contenedor | Docker, imagen base `python:3.12-alpine` | 20.10 | — |
| Pruebas | pytest + httpx (`ASGITransport`) + anyio | — | pytest 9.2 |

## Arquitectura general

```
Cliente HTTP (REST Client, curl, corrector)
        │
        ▼
 uvicorn (0.0.0.0:8000, dentro del contenedor)
        │
        ▼
 FastAPI app (app/main.py)
   ├─ lifespan: crea motor + fábrica de sesiones (app.state), create_all, dispose al apagar
   ├─ routers por módulo (health, editoriales, generos, autores, libros, clientes, ventas)
   │     router.py → recibe y declara la respuesta
   │     service.py → lógica, traducción de errores, lecturas con precarga
   │     schemas.py → DTO Create / Update / Read
   │     models.py → tablas SQLModel
   └─ BackgroundTasks → aviso del comprobante después de responder
        │
        ▼ asyncpg (DATABASE_URL, postgresql+asyncpg://…)
 PostgreSQL 16 (fuera del contenedor)
```

Monolito modular asincrónico: un único proceso con un módulo por funcionalidad, todos con la misma
estructura. La lógica vive en el `service` de cada módulo, que recibe la sesión como parámetro. La base
garantiza unicidad, claves foráneas y comprobaciones; la aplicación traduce sus rechazos a 409.

## Integraciones externas

| Servicio | Propósito | Tipo |
|---|---|---|
| PostgreSQL del VPS | Persistencia | Conexión asyncpg |
| Aviso del comprobante | Simulado: `await asyncio.sleep(0.5)` + log | Tarea en segundo plano (no hay servicio real) |

## API REST

| Recurso | Endpoints |
|---|---|
| Salud | `GET /health/live`, `GET /health/ready` |
| Editoriales | `POST /editoriales/`, `GET /editoriales/`, `GET/PATCH /editoriales/{id}`, `GET /editoriales/{id}/libros` |
| Géneros | `POST /generos/`, `GET /generos/`, `GET /generos/{id}/libros` |
| Autores | `POST /autores/`, `GET /autores/`, `GET/PATCH /autores/{id}`, `GET /autores/{id}/libros` |
| Libros | `POST /libros/`, `GET /libros/?limit&offset&titulo&genero_id`, `GET/PATCH /libros/{id}` |
| Clientes | `POST /clientes/`, `GET/PATCH /clientes/{id}`, `POST /clientes/{id}/perfil`, `GET /clientes/{id}/ventas` |
| Ventas | `POST /ventas/`, `GET /ventas/`, `GET /ventas/{id}` (sin PATCH ni DELETE) |

Códigos: 201 al crear, 404 si el recurso no existe, 409 si la base rechaza la escritura, 422 si el
cuerpo o los parámetros no cumplen el contrato. `/health/ready` responde 503 si la base no responde.
