# Proposal

## Why

La Persona 4 del parcial cierra el flujo de negocio con las **ventas** (Ejercicios 4 y 6; RN-04 a RN-08; casos C-05, C-06 y C-07) y empaqueta y despliega la aplicación (Ejercicios 7 y 8; casos D-01 a D-07). El código ya existe y está probado localmente; este change lo formaliza como especificación verificable y deja explícito qué queda pendiente por falta de Docker en la máquina del grupo y de acceso al VPS de la cátedra.

## What Changes

- `POST /ventas/` con `cliente_id` y `renglones` (`libro_id`, `cantidad`): el servidor copia el precio de cada libro al renglón, calcula subtotales y `total = Σ cantidad × precio` con `Decimal`, y responde 201 con `VentaRead` (caso C-06: total `77000.00`).
- Errores de ventas: libro inexistente → 409 `"No existe el libro con id N."`; cliente inexistente → 409 por clave foránea (C-05); sin renglones, libro repetido, cantidad ≤ 0 o `precio`/`total`/`fecha` en el cuerpo → 422.
- Las ventas son inmutables: el precio del renglón no cambia si cambia el libro (RN-06) y no hay `PATCH` ni `DELETE` (405, RN-08).
- `GET /ventas/` paginado y `GET /ventas/{id}` con una cantidad fija de consultas (C-07).
- Aviso del comprobante con `BackgroundTasks` (`await asyncio.sleep(0.5)` + log) que corre después de responder y no bloquea; la sesión de ventas usa `scope="function"`.
- `app/seed.py` (`python -m app.seed`) deja la base en un estado conocido.
- `Dockerfile` (python:3.12-alpine, dependencias antes del código con `--no-cache-dir`, usuario sin root, `HEALTHCHECK` con `wget` a `127.0.0.1:8000/health/ready`, uvicorn en `0.0.0.0`) y `.dockerignore` sin secretos; se amplía para excluir los artefactos OPSX/KB.
- `README.md`, `DEPLOY.md` (URL, fecha/hora, comandos `docker build`/`docker run` con `--env-file` y `--restart unless-stopped`, cómo se actualiza) y `evidencia/` (C-07 y casos D).
- Los casos D-01..D-07 y el despliegue real quedan **PENDIENTES** hasta tener Docker y acceso al VPS.

## Capabilities

### New Capabilities
- `ventas`: registro de ventas con renglones, precios copiados, total calculado por el servidor, inmutabilidad, consultas con cantidad fija de queries, aviso en segundo plano y datos iniciales.
- `contenedor-y-despliegue`: imagen Docker de la aplicación, ejecución con `docker run`, salud del contenedor, ausencia de secretos y documentación/evidencia del despliegue en el VPS.

### Modified Capabilities
- Ninguna.

## Impact

- Código: `app/modules/ventas/{schemas,service,router}.py`, `app/seed.py`. Los modelos `Venta`/`RenglonVenta` (`app/modules/ventas/models.py`) pertenecen a `base-y-modelos` y no se tocan.
- Pruebas: `tests/test_ventas.py`, `tests/test_datos_iniciales.py`, `test/casos_minimos.http` (C-01..C-08).
- Contenedor y documentación: `Dockerfile`, `.dockerignore`, `README.md`, `DEPLOY.md`, `evidencia/`.
- API: nuevos endpoints `/ventas/`. Sin dependencias nuevas.
- Depende de C-01..C-03 (`base-y-modelos`, `catalogo-editoriales-generos-autores`, `libros-y-clientes`).

## Supuestos

- El código existente es la implementación de referencia: apply verifica y sólo corrige si una tarea falla.
- La suite completa del proyecto tiene 83 pruebas (dato del coordinador).
- Los casos D y el llenado final de `DEPLOY.md` no se pueden ejecutar todavía (sin Docker ni VPS); quedan como tareas `(PENDIENTE VPS)`.
