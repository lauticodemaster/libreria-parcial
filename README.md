# Librería: API con despliegue en el VPS

Parcial de **Programación III** (capítulos 1 a 4). Tecnicatura Universitaria en Programación.

API asincrónica para el catálogo y las ventas de una librería de barrio, hecha con FastAPI, SQLModel,
SQLAlchemy 2 asincrónico, asyncpg y PostgreSQL 16. Se empaqueta en una imagen de Docker sobre
`python:3.12-alpine` y está desplegada en **https://libreria.saferazi.me** (ver [DEPLOY.md](DEPLOY.md)).

## Integrantes

**Grupo Saferazi.** Archivo de entrega: `Parcial_Cap1a4_Saferazi.zip`.

| Integrante | Nombre y apellido | Parte del trabajo |
|---|---|---|
| Persona 1 | Lautaro Fernández | Base del proyecto: estructura, configuración, base de datos, `main.py`, módulo `health` y todos los modelos de tabla |
| Persona 2 | Daniela Díaz | Módulos `editoriales`, `generos` y `autores` |
| Persona 3 | Jesús Ramírez | Módulos `libros` (con `LibroAutor`) y `clientes` (con `PerfilCliente`) |
| Persona 4 | Danilo Serrano | Módulo `ventas` (con `RenglonVenta` y `BackgroundTasks`), datos iniciales, casos C-01 a C-08, Docker, README, DEPLOY y evidencia |

## Cómo levantarlo desde cero (máquina del grupo)

Requisitos: Python 3.12 o superior y PostgreSQL 16 funcionando.

1. **Crear la base** (vacía; las tablas las crea la aplicación al arrancar):

   ```bash
   createdb -U postgres libreria
   ```

2. **Entorno virtual y dependencias**:

   ```bash
   python -m venv .venv
   # Windows (PowerShell):  .venv\Scripts\Activate.ps1
   # Linux / macOS:         source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Archivo `.env`**: copiar `env.example` como `.env` y completar `DATABASE_URL` con el usuario,
   la contraseña, el servidor y el nombre de la base. El `.env` **no se versiona**.

   ```bash
   cp env.example .env      # Windows: copy env.example .env
   ```

   ```env
   DATABASE_URL=postgresql+asyncpg://<usuario>:<contraseña>@localhost:5432/libreria
   SQL_ECHO=false
   ```

   Con `SQL_ECHO=true` la consola muestra cada consulta SQL (sirve para el caso C-07).

4. **Arrancar el servidor**. Al arrancar, el lifespan crea las tablas que falten con `create_all`:

   ```bash
   uvicorn app.main:app --reload
   ```

   Documentación interactiva: <http://localhost:8000/docs>.

5. **Cargar los datos iniciales**. Deja la base en un estado conocido: vacía las tablas, reinicia
   los ids y carga 3 editoriales, 3 géneros, 5 autores, 6 libros, 3 clientes y 1 venta.

   ```bash
   python -m app.seed
   ```

6. **Probar**: abrir los archivos de `test/` con la extensión *REST Client* de VS Code y ejecutar los
   pedidos en orden. Cada pedido tiene la respuesta esperada en un comentario.
   `test/casos_minimos.http` tiene los casos C-01 a C-08 de la consigna.

### Pruebas automáticas (opcional)

Corren contra un PostgreSQL real, en una base de **prueba** distinta de la de trabajo (las pruebas
vacían las tablas antes de cada caso):

```bash
createdb -U postgres libreria_test
pip install -r requirements-dev.txt
# Linux / macOS:
TEST_DATABASE_URL=postgresql+asyncpg://<usuario>:<contraseña>@localhost:5432/libreria_test pytest
# Windows (PowerShell):
$env:TEST_DATABASE_URL="postgresql+asyncpg://<usuario>:<contraseña>@localhost:5432/libreria_test"; pytest
```

Sin `TEST_DATABASE_URL` las pruebas se saltean.

## Estructura

```
app/
├── main.py                  Aplicación, lifespan (motor, sesiones, create_all) y registro de routers
├── seed.py                  Datos iniciales (python -m app.seed)
├── core/
│   ├── config.py            Lectura de DATABASE_URL y SQL_ECHO desde el entorno (.env)
│   ├── database.py          Motor, fábrica de sesiones y dependencia get_session
│   ├── errores.py           Traducción de IntegrityError a mensajes propios (RN-12)
│   └── paginacion.py        limit y offset con sus restricciones (RN-10)
└── modules/
    └── <módulo>/            health, editoriales, generos, autores, libros, clientes, ventas
        ├── models.py        Modelos de tabla, restricciones y relaciones
        ├── schemas.py       DTO de entrada (Create, Update) y de salida (Read)
        ├── service.py       Lógica, traducción de errores y lecturas con precarga
        └── router.py        Rutas HTTP: reciben, delegan y declaran la respuesta
test/                        Archivos .http con los casos de prueba
tests/                       Pruebas automáticas con pytest
evidencia/                   Salidas de consola y capturas de los casos
Dockerfile, .dockerignore    La imagen del proyecto
DEPLOY.md                    Cómo se construyó y se corrió la imagen en el VPS
```

`LibroAutor` vive en `libros`, `PerfilCliente` en `clientes` y `RenglonVenta` en `ventas`.

## Modelo de dominio: de qué lado va cada clave foránea

| Relación | Tipo | Clave foránea | Por qué de ese lado |
|---|---|---|---|
| Libro → Editorial | Agregación | `libro.editorial_id` (NOT NULL) | Muchos libros comparten una editorial que existe por sí misma: la clave va en el lado "muchos". |
| Libro → Género | Agregación opcional | `libro.genero_id` (admite NULL) | Igual que la editorial, pero optativa: un libro puede no tener género. |
| Libro ↔ Autor | Muchos a muchos con datos | `libro_autor.libro_id` y `libro_autor.autor_id` (PK compuesta) | La relación tiene datos propios (rol y orden): se modela como objeto de asociación `LibroAutor`, no con `link_model`. Se navega `libro.autorias[i].autor`. |
| Cliente ↔ PerfilCliente | Uno a uno | `perfil_cliente.cliente_id` UNIQUE | El perfil depende del cliente. El UNIQUE impide un segundo perfil (RN-09). `Cliente.perfil` devuelve un objeto (`uselist=False`). |
| Venta → Cliente | Asociación | `venta.cliente_id` | La venta conoce a su cliente; ninguno es parte del otro. |
| Venta ◆ RenglonVenta | Composición | `renglon_venta.venta_id` (ON DELETE CASCADE) | El renglón no tiene sentido sin su venta y nace con ella (cascade `all, delete-orphan`). |
| RenglonVenta → Libro | Asociación | `renglon_venta.libro_id` | El renglón nombra un libro que ya existe. Su precio se copia al registrar la venta. |

Cada clave foránea tiene índice: `ix_libro_editorial_id`, `ix_libro_genero_id`, `ix_libro_autor_autor_id`,
`ix_venta_cliente_id` e `ix_renglon_venta_libro_id`. En `libro_autor.libro_id`, `perfil_cliente.cliente_id`
y `renglon_venta.venta_id` el índice lo da la clave primaria o el UNIQUE, que empiezan por esa columna.
Todas las relaciones están declaradas en los dos extremos con `back_populates` y con `lazy="raise"`:
ninguna lectura puede depender de la carga perezosa.

## Reglas de negocio y dónde se garantizan

| Regla | Garante |
|---|---|
| RN-01 ISBN único | `uq_libro_isbn` en la base → 409 "Ya existe un libro con ese ISBN." |
| RN-02 Email único | `uq_cliente_email` en la base → 409 "Ya existe un cliente con ese email." |
| RN-03 Precio > 0 y stock ≥ 0 | `ck_libro_precio_positivo`, `ck_libro_stock_no_negativo` y validación del DTO (422) |
| RN-04 La venta se crea con sus renglones | DTO anidado `VentaCreate.renglones`; se agregan a `venta.renglones` en la misma transacción |
| RN-05 Al menos un renglón, sin libros repetidos | Validación del DTO (422) y `uq_renglon_venta_venta_libro` en la base |
| RN-06 El precio se copia del libro | El servidor lo lee de la base; no viaja en el DTO (si viaja, 422) |
| RN-07 El total lo calcula el servidor | Suma de cantidad × precio unitario con `Decimal`; no viaja en el DTO |
| RN-08 Las ventas no se modifican | No hay PATCH ni DELETE de ventas (405) |
| RN-09 Un perfil por cliente | `uq_perfil_cliente_cliente_id` → 409 |
| RN-10 Listados paginados | `limit` de 1 a 100 (20 por defecto) y `offset` desde 0, con restricciones en `Query` → 422 |
| RN-11 Búsqueda por título | `ILIKE` con parámetro ligado (y los comodines `%` y `_` escapados) |
| RN-12 Sin texto interno de la base | `IntegrityError` traducido a un mensaje propio según el nombre de la restricción |

En las altas no se consulta antes si un id existe: se escribe y, si la base rechaza la clave foránea,
se responde 409. La única lectura previa es la del precio de los libros de una venta, que la
consigna exige leer de la base.

## Endpoints

| Método | Ruta | Respuesta |
|---|---|---|
| GET | `/health/live` | `{"estado": "vivo"}` (no toca la base) |
| GET | `/health/ready` | Ejecuta `SELECT 1`; 200 o 503 |
| POST, GET | `/editoriales/` | Alta (201) y listado paginado |
| GET, PATCH | `/editoriales/{id}` | Detalle y modificación parcial |
| GET | `/editoriales/{id}/libros` | Libros de la editorial |
| POST, GET | `/generos/` | Alta y listado |
| GET | `/generos/{id}/libros` | Libros del género |
| POST, GET | `/autores/` | Alta y listado |
| GET, PATCH | `/autores/{id}` | Detalle y modificación parcial |
| GET | `/autores/{id}/libros` | Libros del autor con rol y orden |
| POST, GET | `/libros/` | Alta con autores (detalle del libro) y listado con editorial y género (`titulo`, `genero_id`) |
| GET, PATCH | `/libros/{id}` | Libro con editorial, género y autores |
| POST | `/clientes/` | Alta |
| GET, PATCH | `/clientes/{id}` | Cliente con su perfil |
| POST | `/clientes/{id}/perfil` | Alta del perfil |
| GET | `/clientes/{id}/ventas` | Ventas del cliente |
| POST, GET | `/ventas/` | Alta con renglones (agenda el aviso del comprobante) y listado |
| GET | `/ventas/{id}` | Venta con cliente y renglones |

## Asincronía

Todos los handlers son `async def` y usan la sesión asincrónica; no hay `time.sleep`, `requests` ni
acceso síncrono a la base. Al registrar una venta se agenda con `BackgroundTasks` el aviso del
comprobante (`await asyncio.sleep(0.5)` y un mensaje en el log), que corre después de enviar la
respuesta; mientras tanto el servidor sigue atendiendo otras peticiones. La sesión del alta de venta
se cierra antes de responder (`Depends(get_session, scope="function")`), así la conexión no queda
tomada durante el aviso.
