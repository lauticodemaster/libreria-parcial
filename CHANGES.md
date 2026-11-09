# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **Librería (API de catálogo y ventas)**.
> Cada change es atómico y se corresponde 1 a 1 con el trabajo (y los commits) de una persona del equipo.
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

> **Nota importante**: el código ya está implementado y probado (83 pruebas pytest, 83/83 en verde; el apply de C-04 sumó pruebas estáticas del contenedor, hoy 23: 106/106).
> Por eso, en cada change el `apply` **verifica las tareas contra el código y las pruebas existentes**
> en lugar de escribir código nuevo; el objetivo es dejar documentado el trabajo de cada integrante
> con specs, tareas y trazabilidad hacia la base de conocimiento.

---

## Cómo usar este documento

1. Identificá el change que corresponde a tu parte (columna `C-NN`) y revisá que sus dependencias estén marcadas `[x]`.
2. Leé los archivos de la sección **Leer antes** de ese change en `knowledge-base/`.
3. Ejecutá `/opsx:propose <nombre-del-change>` (por ejemplo `/opsx:propose base-y-modelos`) y luego `/opsx:apply` para verificar las tareas contra el código y las pruebas.
4. Cuando todo esté verificado, `/opsx:archive <nombre-del-change>` para sincronizar las specs y cerrar el change.
5. Marcá el checkbox de **Estado** (`[ ]` → `[x]`) en este archivo.

Specs (capacidades) por change, disjuntas entre sí:

| Change | Capacidades (spec) |
|--------|--------------------|
| `base-y-modelos` | `proyecto-base`, `modelo-de-datos` |
| `catalogo-editoriales-generos-autores` | `catalogo` |
| `libros-y-clientes` | `libros`, `clientes` |
| `ventas-docker-despliegue` | `ventas`, `contenedor-y-despliegue` |

---

## Árbol de dependencias

```
C-01 base-y-modelos                              (Persona 1)
 └── C-02 catalogo-editoriales-generos-autores   (Persona 2)
      └── C-03 libros-y-clientes                 (Persona 3)
           └── C-04 ventas-docker-despliegue     (Persona 4)
```

### Paralelismo por fase

Los commits del equipo son secuenciales, así que **no hay paralelismo entre changes**: cada uno se
desbloquea recién cuando el anterior está archivado.

```
GATE 0: (inicio)
  → C-01 base-y-modelos                              [Agente A]

GATE 1: C-01 ✓
  → C-02 catalogo-editoriales-generos-autores        [Agente A]

GATE 2: C-02 ✓
  → C-03 libros-y-clientes                           [Agente A]

GATE 3: C-03 ✓
  → C-04 ventas-docker-despliegue                    [Agente A]
```

### Camino crítico (4 changes — mínimo irreducible)

`C-01 base-y-modelos` → `C-02 catalogo-editoriales-generos-autores` → `C-03 libros-y-clientes` → `C-04 ventas-docker-despliegue`

### Plan óptimo con 3 agentes

Al ser una cadena lineal, un solo agente trabaja por paso; los otros dos quedan libres.

| Paso | Agente A (Backend Core) | Agente B (Backend Aux) | Agente C (Frontend) |
|------|-------------------------|------------------------|---------------------|
| 1 | C-01 base-y-modelos | — | — |
| 2 | C-02 catalogo-editoriales-generos-autores | — | — |
| 3 | C-03 libros-y-clientes | — | — |
| 4 | C-04 ventas-docker-despliegue | — | — |

---

## FASE 1 — Fundación y modelo de datos

### [C-01] `base-y-modelos`
- **Estado**: `[x]` archivado en `openspec/changes/archive/2026-11-08-base-y-modelos/` (specs `proyecto-base`, `modelo-de-datos`)
- **Scope** (Persona 1; capacidades `proyecto-base`, `modelo-de-datos`):
  - Estructura del proyecto: `app/`, `app/core/`, `app/modules/<7 módulos>/`, `tests/`, `pytest.ini`, `requirements.txt`, `requirements-dev.txt`, `env.example`, `.gitignore`
  - `app/core/config.py` (lee `DATABASE_URL` y `SQL_ECHO`; falla si falta `DATABASE_URL`), `app/core/database.py` (motor async, fábrica de sesiones con `expire_on_commit=False`, `get_session`), `app/core/errores.py` (traducción de `IntegrityError` a 409 con mensajes propios), `app/core/paginacion.py` (`PaginacionDep`)
  - `app/main.py`: lifespan (motor y fábrica en `app.state`, `create_all`, `dispose` al apagar), manejador de `IntegrityError`, registro tolerante de routers
  - Módulo `health`: `GET /health/live` (no toca la base) y `GET /health/ready` (`SELECT 1`, 503 si la base no responde)
  - `models.py` de los 7 módulos: tablas `editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta`, `renglon_venta`; restricciones UNIQUE/CHECK/FK, índices `ix_*`, relaciones con `back_populates` y `lazy="raise"`
  - `tests/conftest.py`: fixtures contra PostgreSQL real (`TEST_DATABASE_URL`), limpieza entre pruebas
  - Tests: salud, arranque con esquema, restricciones del modelo
  - Gestión de configuración y secretos: **sensibilidad ALTA** (`DATABASE_URL` y `TEST_DATABASE_URL` nunca en el repositorio; `env.example` sólo con la forma)
- **Dependencias**: ninguna
- **Governance**: MEDIO (modelo de datos y configuración; el manejo de secretos/config se trata con sensibilidad ALTA)
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md`
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados, §Seguridad, §Variables de entorno
  - `knowledge-base/07_flujos_principales.md` §Flujo 1
  - `knowledge-base/06_funcionalidades.md` §Épica 1 (US-001, US-002)
  - `knowledge-base/09_decisiones_y_supuestos.md`

---

## FASE 2 — Catálogo base

### [C-02] `catalogo-editoriales-generos-autores`
- **Estado**: `[x]` archivado en `openspec/changes/archive/2026-11-08-catalogo-editoriales-generos-autores/` (spec `catalogo`)
- **Scope** (Persona 2; capacidad `catalogo`):
  - `schemas.py`, `service.py`, `router.py` de `editoriales`, `generos` y `autores` (DTO Create/Update/Read, `extra="forbid"` en las altas)
  - Editoriales: alta (201/409/422), listado paginado, detalle (404), `PATCH` parcial con `exclude_unset`, libros de la editorial
  - Géneros: alta (409 si el nombre se repite), listado, libros del género (404 si no existe)
  - Autores: alta, detalle, `PATCH` parcial, libros del autor con rol y orden
  - Reglas: unicidad de nombre resuelta por la base (RN-10, RN-12, RT-CAT-01), sin consultar antes de escribir
  - Tests: altas, duplicados, 404, PATCH parcial, paginación, listados de libros
- **Dependencias**: `C-01`
- **Governance**: BAJO (CRUDs simples de catálogo)
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 2 (US-010 a US-012)
  - `knowledge-base/05_reglas_de_negocio.md` (RN-10, RN-12, RT-CAT-01)
  - `knowledge-base/04_modelo_de_datos.md` §editorial, §genero, §autor
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados

---

## FASE 3 — Libros y clientes

### [C-03] `libros-y-clientes`
- **Estado**: `[x]` archivado en `openspec/changes/archive/2026-11-08-libros-y-clientes/` (specs `libros`, `clientes`)
- **Scope** (Persona 3; capacidades `libros`, `clientes`):
  - Libros: `POST /libros/` con autorías `LibroAutor` (rol, orden), 201 con `LibroDetalle`; 409 por ISBN repetido o id inexistente (mensaje según la FK); 422 por precio, stock, rol u orden inválidos y autores repetidos
  - Libros: listado paginado con editorial y género, búsqueda por título sin distinguir mayúsculas con **parámetro ligado** (la entrada de inyección SQL devuelve 200 con lista vacía), filtro por género
  - Libros: detalle sin N+1 (`joinedload` + `selectinload`, cantidad fija de consultas)
  - Clientes: alta (409 si el email se repite), detalle con perfil como objeto (uno a uno), `PATCH` parcial, alta del perfil (409 si ya tiene; 404 si el cliente no existe), ventas del cliente
  - Reglas: RN-01, RN-02, RN-03, RN-09, RN-10, RN-11, RT-GL-01, RT-GL-02
  - Tests: contrato 422, 409 por ISBN/FK, búsqueda segura, conteo de consultas, perfil 1:1
- **Dependencias**: `C-02`
- **Governance**: MEDIO (lógica de negocio, carga anticipada y consultas parametrizadas)
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 3 (US-020 a US-023)
  - `knowledge-base/07_flujos_principales.md` §Flujo 2
  - `knowledge-base/05_reglas_de_negocio.md` (RN-01 a RN-03, RN-09 a RN-11)
  - `knowledge-base/04_modelo_de_datos.md` §libro, §libro_autor, §cliente, §perfil_cliente
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad

---

## FASE 4 — Ventas y despliegue

### [C-04] `ventas-docker-despliegue`
- **Estado**: `[x]` archivado en `openspec/changes/archive/2026-11-08-ventas-docker-despliegue/` (specs `ventas`, `contenedor-y-despliegue`). Las 9 tareas que esperaban el VPS (5.3 y 6.1–6.8) se completaron el 08/11/2026 con el despliegue en https://libreria.saferazi.me
- **Scope** (Persona 4; capacidades `ventas`, `contenedor-y-despliegue`):
  - Ventas: `POST /ventas/` con `cliente_id` y renglones; el servidor copia `precio_unitario` desde el libro y calcula `total = Σ cantidad × precio`; 201 con `VentaRead`; 409 si el libro o el cliente no existen; 422 sin renglones, libro repetido, cantidad ≤ 0 o precio/total/fecha en el cuerpo
  - `BackgroundTasks`: aviso del comprobante (`await asyncio.sleep(0.5)` + log) que corre después de responder
  - `app/seed.py` (`python -m app.seed`: `TRUNCATE … RESTART IDENTITY CASCADE` y datos iniciales)
  - `test/casos_minimos.http` (casos C-01 a C-08)
  - `Dockerfile` sobre `python:3.12-alpine`, `USER libreria`, `HEALTHCHECK`, `.dockerignore` (sin secretos en la imagen)
  - `README.md`, `DEPLOY.md` (casos D-01 a D-07), carpeta `evidencia/`; casos D hechos en el servidor del grupo (https://libreria.saferazi.me)
  - Tests: precio copiado, total, 409/422, aviso en segundo plano, seed
  - Despliegue: secretos sólo vía `--env-file`; **sensibilidad ALTA** en el manejo de `DATABASE_URL` en el VPS
- **Dependencias**: `C-03`
- **Governance**: MEDIO (ventas); el despliegue se trata como ALTO por el manejo de secretos
- **Leer antes**:
  - `knowledge-base/06_funcionalidades.md` §Épica 4 (US-030 a US-033)
  - `knowledge-base/07_flujos_principales.md` §Flujo 3, §Flujo 4
  - `knowledge-base/11_contenedor_y_despliegue.md`
  - `knowledge-base/05_reglas_de_negocio.md` (RN-04 a RN-08)
  - `knowledge-base/10_preguntas_abiertas.md`

---

## Resumen

| ID | Change | Persona | Dependencias | Governance |
|----|--------|---------|--------------|------------|
| C-01 | `base-y-modelos` | 1 | — | MEDIO (config/secretos ALTO) |
| C-02 | `catalogo-editoriales-generos-autores` | 2 | C-01 | BAJO |
| C-03 | `libros-y-clientes` | 3 | C-02 | MEDIO |
| C-04 | `ventas-docker-despliegue` | 4 | C-03 | MEDIO (deploy ALTO) |

**Estado final (09/11/2026)**: los 4 changes hicieron el ciclo completo (propose → apply → archive); `openspec list` no muestra changes activos y las 7 specs están en `openspec/specs/`. C-04 tiene sus 22 tareas completas: el proyecto quedó desplegado y los casos D tienen evidencia.
