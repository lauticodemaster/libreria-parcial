# Funcionalidades

Organizadas por épica. Las épicas coinciden con las partes del reparto y con los changes de OPSX
(ver `CHANGES.md`).

## Épica 1: Base del proyecto y modelo de datos

### US-001 — Salud de la aplicación
**Como** operador del despliegue **quiero** `GET /health/live` (no toca la base) y `GET /health/ready`
(ejecuta `SELECT 1`) **para** saber si el proceso vive y si llega a su base.
**Criterios de aceptación**:
- [x] `/health/live` → 200 `{"estado": "vivo"}`.
- [x] `/health/ready` → 200 `{"estado": "listo", "base": "ok"}`; 503 si la base no responde.

### US-002 — Arranque con esquema
**Como** operador **quiero** que la aplicación cree las tablas que falten al arrancar **para** levantarla
sobre una base vacía sin migraciones.
**Criterios de aceptación**:
- [x] El lifespan crea motor y fábrica de sesiones en `app.state`, ejecuta `create_all` y cierra el motor.
- [x] Sin `DATABASE_URL` o sin base, el arranque falla con error.
**Reglas relacionadas**: RT-GL-05.

## Épica 2: Catálogo (editoriales, géneros y autores)

### US-010 — Editoriales
**Como** personal **quiero** dar de alta, listar, ver, modificar parcialmente editoriales y ver sus
libros. **Criterios**: 201/409/422 en el alta; 404 si no existe; PATCH con `exclude_unset`.
### US-011 — Géneros
Alta (409 si se repite), listado y libros del género (404 si no existe).
### US-012 — Autores
Alta, detalle, PATCH parcial y libros del autor con rol y orden.
**Reglas relacionadas**: RN-10, RN-12, RT-CAT-01.

## Épica 3: Libros y clientes

### US-020 — Alta de libro con autorías
**Como** personal **quiero** dar de alta un libro con los ids de editorial, género y autores, más el rol
y el orden de cada autoría **para** registrar el catálogo completo en un pedido.
**Criterios**: 201 con el detalle; 409 si el ISBN se repite o un id no existe (C-02, C-04); 422 si el
precio, el stock, el rol o el orden no cumplen el contrato.
**Reglas relacionadas**: RN-01, RN-03, RT-GL-01.

### US-021 — Listado y búsqueda de libros
Listado con editorial y género, paginado, filtrable por título (sin distinguir mayúsculas) y género.
C-08: `' OR '1'='1` → 200 con lista vacía. **Reglas**: RN-10, RN-11.

### US-022 — Detalle de libro sin N+1
Libro con editorial, género y autores en una cantidad fija de consultas (C-07). **Reglas**: RT-GL-02.

### US-023 — Clientes y perfil
Alta (409 si el email se repite, C-02), detalle con su perfil como objeto, PATCH parcial, alta del perfil
(409 si ya tiene uno, C-03; 404 si el cliente no existe) y ventas del cliente.
**Reglas relacionadas**: RN-02, RN-09.

## Épica 4: Ventas, contenedor y despliegue

### US-030 — Registrar una venta
**Como** personal **quiero** registrar una venta con el id del cliente y sus renglones **para** que el
servidor copie los precios y calcule el total.
**Criterios**: 201 con cliente, renglones, precios copiados y total (C-06); 409 si el libro o el cliente
no existen (C-05); 422 sin renglones, con un libro repetido o si viajan precio, total o fecha.
**Reglas relacionadas**: RN-04 a RN-08.

### US-031 — Aviso del comprobante
Se agenda con `BackgroundTasks`, corre después de responder (`await asyncio.sleep(0.5)` + log) y no
bloquea al servidor.

### US-032 — Datos iniciales
`python -m app.seed` deja la base en un estado conocido.

### US-033 — Imagen y despliegue
Imagen sobre `python:3.12-alpine`, sin root, sin secretos, con HEALTHCHECK; corre con `docker run` y
`--env-file`; se despliega en el VPS y se documenta en `DEPLOY.md` (casos D-01 a D-07).
