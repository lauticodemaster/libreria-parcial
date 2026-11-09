# Flujos Principales

## Flujo 1: Arranque de la aplicación

**Disparador**: `uvicorn app.main:app` (o el `CMD` del contenedor). **Actor**: operador.

1. `main.py` importa todos los modelos y registra los routers de los 7 módulos.
2. El lifespan lee `DATABASE_URL` y `SQL_ECHO` (`app/core/config.py`).
3. Crea el motor asincrónico y la fábrica de sesiones (`expire_on_commit=False`) y los guarda en `app.state`.
4. Ejecuta `SQLModel.metadata.create_all`: crea sólo las tablas que faltan.
5. Atiende pedidos. Al apagar, `motor.dispose()`.

**Casos de error**: sin `DATABASE_URL` → `RuntimeError`, uvicorn termina con código 3; base caída →
`ConnectionRefusedError`, termina con código 3 (el contenedor no queda atendiendo sin base).

## Flujo 2: Alta de libro con autorías

**Disparador**: `POST /libros/`. **Actor**: personal.

1. FastAPI valida `LibroCreate` (precio > 0, stock ≥ 0, rol válido, orden ≥ 1, autores sin repetir).
2. El service arma `Libro` con sus `LibroAutor` y hace commit. **No** consulta antes si los ids existen.
3. Relee el detalle con `joinedload(editorial, genero)` + `selectinload(autorias).joinedload(autor)`.
4. Responde 201 con `LibroDetalle`.

**Casos de error**: ISBN repetido → 409 "Ya existe un libro con ese ISBN."; editorial, género o autor
inexistente → 409 con mensaje propio según el nombre de la clave foránea; contrato → 422.

## Flujo 3: Registro de una venta

**Disparador**: `POST /ventas/` con `cliente_id` y `renglones`. **Actor**: personal.

```
Cliente → API (VentaCreate) → service.crear
            SELECT id, precio FROM libro WHERE id IN (…)      ← precios
            INSERT venta + renglones (precio copiado, total = Σ cantidad×precio)
            COMMIT  (FK de cliente rechazada → 409)
            SELECT venta + cliente / renglones + libro         ← detalle (2 consultas)
        ← 201 VentaRead
        … después de responder: BackgroundTasks → sleep(0.5) → log "Comprobante de la venta N…"
```

**Casos de error**: libro inexistente → 409 "No existe el libro con id N."; cliente inexistente → 409
"El cliente indicado no existe."; sin renglones, libro repetido, cantidad ≤ 0, o precio/total/fecha en
el cuerpo → 422.

## Flujo 4: Despliegue y actualización en el VPS

1. `docker build -t libreria .` (en el VPS, desde el repositorio).
2. `docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped --env-file ~/libreria.env libreria`
   (con `--add-host=host.docker.internal:host-gateway` si la base corre en el propio VPS).
3. `docker exec libreria python -m app.seed`.
4. Para actualizar: `git pull`, `docker build`, `docker rm -f libreria`, el mismo `docker run`. Los datos
   siguen porque viven en la base del servidor.
