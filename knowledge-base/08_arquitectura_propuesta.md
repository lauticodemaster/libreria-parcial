# Arquitectura Propuesta

## Patrones aplicados

| Patrón | Dónde se usa | Por qué |
|---|---|---|
| Módulo funcional (vertical slice) | `app/modules/<módulo>/{models,schemas,service,router}.py` | Estructura obligatoria de la consigna; cada módulo es autocontenido |
| DTO separados de las tablas | `schemas.py` (Create, Update, Read) vs `models.py` | Los DTO de alta no llevan id; la salida no expone la tabla |
| Inyección de dependencias | `Depends(get_session)`, `PaginacionDep` | Una sesión por petición; paginación declarada una vez |
| Lifespan con estado | `app.state.motor`, `app.state.fabrica_sesiones` | Recursos creados al arrancar y liberados al apagar |
| Objeto de asociación | `LibroAutor` | El muchos a muchos tiene datos propios (rol, orden) |
| Carga anticipada | `joinedload` / `selectinload` + `lazy="raise"` | Número fijo de consultas, sin N+1 |
| La base como garante | UNIQUE / FK / CHECK + `app/core/errores.py` | Sin carreras entre "consultar y escribir"; mensajes propios (RN-12) |
| Tarea en segundo plano | `BackgroundTasks` en el alta de venta | El aviso corre después de responder |

## Estructura de directorios

```
app/
├── main.py            lifespan, manejador de IntegrityError, registro de routers
├── seed.py            datos iniciales
├── core/              config.py, database.py, errores.py, paginacion.py
└── modules/
    ├── health/        models (sin tablas), schemas, service, router
    ├── editoriales/   ├── generos/   ├── autores/
    ├── libros/        (Libro + LibroAutor)
    ├── clientes/      (Cliente + PerfilCliente)
    └── ventas/        (Venta + RenglonVenta)
test/        archivos .http (C-01 a C-08)
tests/       pytest contra PostgreSQL real (TEST_DATABASE_URL)
evidencia/   salidas de consola y capturas
openspec/    especificaciones y changes de OPSX
```

## Seguridad

- Autenticación / autorización: fuera de alcance (capítulo 5).
- Validación de input: Pydantic en los DTO (`extra="forbid"` en las altas), restricciones en `Query` y
  tipos en la ruta (422 sin ejecutar el handler).
- SQL: siempre con parámetros ligados; nunca concatenación de texto con datos del usuario.
- Errores: mensajes propios; nunca el texto de la base ni una traza.
- Secretos: `.env` fuera del repositorio (`.gitignore`) y fuera de la imagen (`.dockerignore`); en el VPS
  entran con `--env-file`. `env.example` sólo tiene la forma.
- Contenedor: usuario sin privilegios (`USER libreria`), imagen base mínima (`python:3.12-alpine`).

## Variables de entorno

| Variable | Descripción | Ejemplo | Sensible |
|---|---|---|---|
| `DATABASE_URL` | Dirección de la base, driver `postgresql+asyncpg` | `postgresql+asyncpg://<usuario>:<contraseña>@<servidor>:5432/<base>` | Sí |
| `SQL_ECHO` | `true` escribe cada consulta en la consola (diagnóstico, C-07) | `false` | No |
| `TEST_DATABASE_URL` | Base de **prueba** para pytest (se vacía en cada prueba) | `postgresql+asyncpg://…/libreria_test` | Sí |
