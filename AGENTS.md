# Librería — Instrucciones para Agentes

API FastAPI asincrónica para el catálogo y las ventas de una librería de barrio (Parcial de
Programación III, capítulos 1 a 4). Se empaqueta en una imagen `python:3.12-alpine` y está desplegada
en https://libreria.saferazi.me con `docker run --env-file`.

## Stack Tecnológico

| Capa | Tecnología | Versión fijada |
|---|---|---|
| Lenguaje | Python | 3.12 |
| Framework web | FastAPI (`fastapi[standard]`), handlers `async def` | 0.162.2 |
| Modelos y contratos | SQLModel | 0.0.48 |
| ORM | SQLAlchemy 2 asincrónico (`SQLAlchemy[asyncio]`) | 2.1.8 |
| Controlador | asyncpg | 0.32.0 |
| Base de datos | PostgreSQL | 16 |
| Configuración | python-dotenv | 1.2.4 |
| Pruebas | pytest + httpx (`ASGITransport`) + anyio, contra PostgreSQL real | pytest 9.2 |
| Contenedor | Docker, base `python:3.12-alpine` | — |

## Base de Conocimiento

| Archivo | Para qué |
|---|---|
| [knowledge-base/README.md](knowledge-base/README.md) | Índice y resumen ejecutivo |
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Alcance y fuera de alcance |
| [02_descripcion_general.md](knowledge-base/02_descripcion_general.md) | Stack, arquitectura, endpoints |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Actores (sin autenticación) |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Tablas obligatorias, restricciones, relaciones, datos iniciales |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | RN-01 a RN-12 y reglas técnicas |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Épicas e historias |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | Arranque, alta de libro, venta, despliegue |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Patrones, seguridad, variables de entorno |
| [09_decisiones_y_supuestos.md](knowledge-base/09_decisiones_y_supuestos.md) | Decisiones DD-01 a DD-09 |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | Inconsistencias y preguntas abiertas |
| [11_contenedor_y_despliegue.md](knowledge-base/11_contenedor_y_despliegue.md) | Dockerfile y casos D |

Antes de codear revisá [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md).

## Skills Disponibles

| Agente | Rol | Skills que carga |
|---|---|---|
| Backend (apply) | Implementar o verificar tareas de un change con TDD | `tdd`, `openspec-apply-change` |
| Planificación | Explorar, proponer y ajustar changes | `openspec-explore`, `openspec-propose`, `openspec-update-change` |
| Cierre | Sincronizar specs y archivar | `openspec-sync-specs`, `openspec-archive-change` |
| Fundación | KB, roadmap, instrucciones y skills | `kb-creator`, `roadmap-generator`, `agent-instruction`, `find-skill` |

Recomendadas por `find-skill` y **no instaladas**: `fastapi`,
`fastapi-templates`, `python-testing-patterns`, `postgresql-table-design`, `postgresql-code-review`,
`python-pro`.

## Roadmap de Changes

Ver [CHANGES.md](CHANGES.md). Cuatro changes en cadena, uno por integrante y por commit:

| ID | Change | Persona | Specs | Governance |
|---|---|---|---|---|
| C-01 | `base-y-modelos` | 1 | `proyecto-base`, `modelo-de-datos` | MEDIO (config y secretos: ALTO) |
| C-02 | `catalogo-editoriales-generos-autores` | 2 | `catalogo` | BAJO |
| C-03 | `libros-y-clientes` | 3 | `libros`, `clientes` | MEDIO |
| C-04 | `ventas-docker-despliegue` | 4 | `ventas`, `contenedor-y-despliegue` | MEDIO (despliegue: ALTO) |

El código ya existe y está probado: el `apply` de cada change verifica sus tareas contra el código y las
pruebas (83/83; con las 16 pruebas estáticas del contenedor que sumó C-04, 99/99). El proyecto está desplegado en https://libreria.saferazi.me (servidor del grupo) y los casos D-01 a D-07 tienen su evidencia en `evidencia/`.

## Reglas Duras (específicas del proyecto)

> Acá viven las reglas **específicas de este proyecto**.

Tomadas de la consigna del parcial:

1. **NUNCA** renombrar ni quitar tablas o columnas del modelo de dominio (`editorial`, `genero`, `autor`,
   `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`) → sólo se pueden agregar
   columnas.
2. **NUNCA** romper la estructura `app/main.py`, `app/core/{config,database}.py` y
   `app/modules/<módulo>/{models,schemas,service,router}.py` → `LibroAutor` vive en `libros`,
   `PerfilCliente` en `clientes`, `RenglonVenta` en `ventas`.
3. **NUNCA** leer una relación con carga perezosa → `joinedload` para relaciones a uno y `selectinload` para
   colecciones, en la misma consulta. Las relaciones tienen `lazy="raise"`.
4. **NUNCA** representar dinero con `float` → `Decimal` y `NUMERIC(10,2)` / `NUMERIC(12,2)`.
5. **NUNCA** verificar unicidad o existencia de un id con una consulta previa → escribir y traducir el
   `IntegrityError` a 409 con mensaje propio (por nombre de restricción). Única excepción: leer el precio
   de los libros al registrar una venta.
6. **NUNCA** devolver al cliente texto interno de la base ni trazas (RN-12).
7. **NUNCA** armar SQL concatenando texto con datos del usuario → parámetros ligados.
8. **NUNCA** usar llamadas bloqueantes en handlers (`time.sleep`, `requests`, acceso síncrono a la base)
   → todo `async def`.
9. **NUNCA** poner una contraseña o un `.env` en el código, el repositorio, la imagen o el zip →
   `env.example` sólo con la forma; en el VPS, `--env-file`.
10. **NUNCA** cambiar la imagen base ni correr como root → `python:3.12-alpine`, `USER` sin privilegios,
    `HEALTHCHECK` con `wget` a `http://127.0.0.1:8000/health/ready`, requirements antes del código con
    `--no-cache-dir`.
11. **NUNCA** agregar PATCH o DELETE de ventas (RN-08), ni aceptar precio, total o fecha en el alta de venta.
12. **NUNCA** correr las pruebas contra la base de trabajo → `TEST_DATABASE_URL` apunta a una base de
    prueba (las pruebas vacían las tablas).
13. Python: `snake_case`, type hints, DTO de alta con `extra="forbid"` y PATCH con `exclude_unset`.
14. Git: cada integrante hace sus propios commits y push, en el orden del reparto.

## Flujo de Trabajo

1. Leer la KB (`knowledge-base/`) y `CHANGES.md`.
2. `/opsx:propose <change>` → proposal, design, tasks y delta specs.
3. `/opsx:apply <change>` → TDD estricto; la suite tiene que quedar en verde.
4. `/opsx:archive <change>` → sincroniza las specs en `openspec/specs/` y cierra el change.
