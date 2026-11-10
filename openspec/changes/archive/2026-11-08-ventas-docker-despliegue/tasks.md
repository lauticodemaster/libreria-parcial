# Tasks

> El código de este change ya existe y está probado. Cada tarea se verifica con el criterio indicado. Las marcadas **(PENDIENTE VPS)** requieren Docker y acceso al VPS, que el grupo todavía no tiene: apply las deja sin marcar, con la justificación, hasta el despliegue.

## 1. Ventas: contrato y alta

- [x] 1.1 Verificar `app/modules/ventas/schemas.py`: `VentaCreate`/`RenglonCreate` con `extra="forbid"`, `renglones` con `min_length=1`, `cantidad > 0` y validador de libro repetido; `VentaRead`/`RenglonRead` con `subtotal` cuantizado. Verifica: `pytest tests/test_ventas.py -k 422` pasa (sin renglones, repetido, cantidad ≤ 0, precio/total/fecha en el cuerpo).
- [x] 1.2 Verificar `crear` en `app/modules/ventas/service.py`: precios leídos en una consulta, 409 `"No existe el libro con id N."`, total `Decimal` = Σ cantidad × precio, cliente inexistente → 409 por FK. Verifica: `pytest tests/test_ventas.py -k "c06 or c05"` pasa (total `77000.00`).
- [x] 1.3 Verificar inmutabilidad (RN-06, RN-08): el precio del renglón no cambia al cambiar el libro y `PATCH`/`DELETE /ventas/{id}` → 405. Verifica: `pytest tests/test_ventas.py -k "precio_del_renglon or no_se_modifican"` pasa.

## 2. Ventas: consultas y segundo plano

- [x] 2.1 Verificar `GET /ventas/` paginado y `GET /ventas/{id}` (404 / 422) en `app/modules/ventas/router.py` y `service.py`. Verifica: `pytest tests/test_ventas.py -k "listado or detalle_404"` pasa.
- [x] 2.2 Verificar C-07: el detalle usa 2 consultas fijas con uno o varios renglones. Verifica: `pytest tests/test_ventas.py -k c07` pasa y `evidencia/C-07_consultas_detalle_libro_y_venta.txt` muestra las consultas.
- [x] 2.3 Verificar el aviso con `BackgroundTasks` (`await asyncio.sleep(0.5)` + log después de responder) y la sesión con `scope="function"`. Verifica: `pytest tests/test_ventas.py -k aviso` pasa (corre en segundo plano y no bloquea).

## 3. Datos iniciales y casos mínimos

- [x] 3.1 Verificar `app/seed.py` (`python -m app.seed`: `TRUNCATE … RESTART IDENTITY CASCADE` y datos conocidos). Verifica: `pytest tests/test_datos_iniciales.py` pasa (3 pruebas, incluida la venta de 77000).
- [x] 3.2 Verificar `test/casos_minimos.http` con C-01..C-08 y su evidencia (`evidencia/C-01_a_C-08_*`). Verifica: cada caso tiene pedido, resultado esperado y salida guardada.

## 4. Imagen Docker

- [x] 4.1 Revisar estáticamente `Dockerfile` contra el Ejercicio 7: `FROM python:3.12-alpine`, `requirements.txt` antes del código con `--no-cache-dir`, usuario sin root + `USER`, `HEALTHCHECK` con `wget` a `http://127.0.0.1:8000/health/ready`, uvicorn `app.main:app` en `0.0.0.0:8000`, sin secretos. Verifica: lectura del archivo punto por punto.
- [x] 4.2 Actualizar `.dockerignore` para excluir `openspec/`, `knowledge-base/`, `CHANGES.md`, `AGENTS.md` y `DEPLOY.md`, manteniendo `.env`, `*.env`, `.venv/`, `.git/` y `**/__pycache__/`. Verifica: `grep` de cada entrada en `.dockerignore`.
- [x] 4.3 Verificar `evidencia/dependencias_alpine_sin_compilar.txt` (todas las dependencias con wheel musllinux). Verifica: el archivo no muestra compilaciones ni errores.

## 5. Documentación

- [x] 5.1 Verificar `README.md`: integrantes y pasos desde cero (entorno virtual, dependencias, `.env`, arranque que crea las tablas, `python -m app.seed`). Verifica: lectura contra el formato de entrega.
- [x] 5.2 Verificar `DEPLOY.md`: comandos `docker build`/`docker run` completos con `--env-file` y `--restart unless-stopped`, nota de `host.docker.internal`, cómo se actualiza y tabla de casos D. Verifica: lectura contra el Ejercicio 8.
- [x] 5.3 (VPS, hecho el 08/11/2026) Completar en `DEPLOY.md` la URL pública, día y hora del despliegue y los cambios hechos para el contenedor. Verifica: `grep -c COMPLETAR DEPLOY.md` da 0.

## 6. Casos D y despliegue

- [x] 6.1 (VPS, hecho el 08/11/2026) D-01: `docker images python:3.12-alpine` y `docker images libreria` → `evidencia/D-01_docker_images.txt` (base < 100 MB).
- [x] 6.2 (VPS, hecho el 08/11/2026) D-02: `docker build` + `docker run` en servidor limpio, `docker ps` `healthy`, `docker logs` con las tablas creadas → `evidencia/D-02_build_run_ps_logs.txt`.
- [x] 6.3 (VPS, hecho el 08/11/2026) Cargar los datos iniciales con `docker exec libreria python -m app.seed`. Verifica: salida sin errores y `GET /libros/` con los libros del seed.
- [x] 6.4 (VPS, hecho el 08/11/2026) D-03: desde afuera, `/health/ready` 200, `/libros/` 200 y venta C-06 201 con `77000.00` → `evidencia/D-03_desde_afuera.txt`.
- [x] 6.5 (VPS, hecho el 08/11/2026) D-04: `docker rm -f libreria` + el mismo `docker run`; vuelve a `healthy` y los datos siguen → `evidencia/D-04_recrear_contenedor.txt`.
- [x] 6.6 (VPS, hecho el 08/11/2026) D-05: correr sin `DATABASE_URL` (sin `--restart`); termina con código ≠ 0 → `evidencia/D-05_sin_database_url.txt`.
- [x] 6.7 (VPS, hecho el 08/11/2026) D-06: `docker exec libreria id` con `uid` ≠ 0 → `evidencia/D-06_usuario.txt`.
- [x] 6.8 (VPS, hecho el 08/11/2026) D-07: `docker logs libreria` con el aviso después de `POST /ventas/ ... 201` → `evidencia/D-07_aviso_en_logs.txt`.

## 7. Verificación final

- [x] 7.1 Correr la suite completa con `pytest`. Verifica: 83/83 pasan (más las 16 pruebas estáticas nuevas de `tests/test_contenedor.py`: 99/99).

## Verificación (apply, 09/11/2026)

- Suite completa contra PostgreSQL 16.2 (`TEST_DATABASE_URL`): **99 passed** (las 83 previas + 16 nuevas).
- `test/casos_minimos.http` contra uvicorn después de `python -m app.seed`: los 15 pedidos dan el código esperado.
- **Hueco encontrado (tarea 4.2) y corregido con TDD**: el `.dockerignore` no excluía los artefactos OPSX y de la
  KB. RED: `tests/test_contenedor.py` (comprobaciones estáticas del Dockerfile y del `.dockerignore`) falló en
  las 5 entradas faltantes (`openspec/`, `knowledge-base/`, `CHANGES.md`, `AGENTS.md`, `DEPLOY.md`).
  GREEN: se agregaron al `.dockerignore`; el resto de los `.md` de la raíz ya quedaban afuera por `*.md`.
  La misma prueba deja verificado estáticamente el punto 4.1 (base alpine, orden de capas, `--no-cache-dir`,
  `USER`, HEALTHCHECK con 127.0.0.1, uvicorn en 0.0.0.0, sin dirección de base).
- **Pendiente (9 tareas, PENDIENTE VPS)**: 5.3 y 6.1 a 6.8 necesitan Docker y los datos de acceso al VPS de la
  cátedra; la máquina del grupo no tiene Docker. Quedan sin marcar a propósito y se cierran en un change o commit
  posterior al despliegue. `DEPLOY.md` tiene los comandos y los lugares `[COMPLETAR]`.

## Verificación del despliegue (08/11/2026)

Las 9 tareas que esperaban el VPS se hicieron en el servidor del grupo (saferazi), porque la cátedra todavía no
entregó el suyo. Base PostgreSQL 16 propia en el contenedor `libreria-db` (volumen y red propios, sin puertos
publicados); la aplicación publica sólo en `127.0.0.1:8090` y Traefik la sirve en **https://libreria.saferazi.me**.

- 5.3: `DEPLOY.md` tiene la URL, la fecha y hora (08/11/2026 23:42), los comandos completos y los cambios; no
  quedan marcadores `[COMPLETAR]`.
- 6.1 D-01: `python:3.12-alpine` 74.8 MB en disco; `libreria:latest` 250 MB.
- 6.2 D-02: build sin compilar nada; `healthy` a los 45 s; los logs muestran el arranque con las tablas creadas.
- 6.3: `docker exec libreria python -m app.seed` sin errores.
- 6.4 D-03: desde la PC del grupo, 200 / 200 / 201 con total `77000.00` (venta 2).
- 6.5 D-04: `docker rm -f` + el mismo `docker run`: `healthy` otra vez y las ventas 1 y 2 siguen.
- 6.6 D-05: sin `DATABASE_URL`, el contenedor termina con código 3.
- 6.7 D-06: `uid=100(libreria)`.
- 6.8 D-07: el aviso de la venta 2 aparece justo después de `POST /ventas/ ... 201 Created`.

Evidencia: `evidencia/D-01` a `D-07` (`.txt` y `.png`) y `evidencia/datos_iniciales_en_el_contenedor`.

