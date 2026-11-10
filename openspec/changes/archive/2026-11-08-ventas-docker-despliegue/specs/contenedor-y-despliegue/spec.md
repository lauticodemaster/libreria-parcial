# Spec Delta

## Purpose

Empaquetar la aplicación en una imagen Docker liviana, segura y sin secretos, ejecutarla con docker run en el VPS de la cátedra y documentar el despliegue con evidencia verificable.

## ADDED Requirements

### Requirement: Imagen basada en python:3.12-alpine
La imagen SHALL construirse con un `Dockerfile` que parte de `python:3.12-alpine` (base menor a 100 MB) e instala `requirements.txt` con `--no-cache-dir` antes de copiar el código, de modo que un cambio sólo en el código reutilice la capa de dependencias.

#### Scenario: Imagen base y de proyecto (D-01)
- **WHEN** se ejecutan `docker images python:3.12-alpine` y `docker images libreria`
- **THEN** la base ocupa menos de 100 MB y la primera instrucción del `Dockerfile` es `FROM python:3.12-alpine`

### Requirement: Proceso sin privilegios
El proceso de la aplicación MUST correr con un usuario sin privilegios dentro del contenedor.

#### Scenario: Usuario del proceso (D-06)
- **WHEN** se ejecuta `docker exec libreria id`
- **THEN** el `uid` es distinto de 0

### Requirement: Imagen sin secretos
La imagen MUST NOT contener secretos ni artefactos que no necesita para correr: el `.dockerignore` excluye `.env`, `.venv`, `.git`, los `__pycache__`, pruebas, evidencia y los artefactos de planificación (`openspec/`, `knowledge-base/`, `CHANGES.md`, `AGENTS.md` y `DEPLOY.md`). La dirección de la base entra sólo como variable de entorno al correr el contenedor.

#### Scenario: Contexto de construcción limpio
- **WHEN** se construye la imagen en una carpeta que tiene `.env` y artefactos OPSX/KB
- **THEN** ninguno de esos archivos queda dentro de la imagen y el `Dockerfile` no menciona `DATABASE_URL` ni contraseñas

### Requirement: Arranque y salud del contenedor
El contenedor SHALL levantar uvicorn con `app.main:app` en `0.0.0.0:8000`, crear las tablas al arrancar y declarar un `HEALTHCHECK` sobre `http://127.0.0.1:8000/health/ready`. Si falta `DATABASE_URL` o la base no responde, el contenedor MUST terminar con error.

#### Scenario: Servidor limpio (D-02)
- **WHEN** en un servidor limpio se ejecutan `docker build -t libreria .` y `docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped --env-file <archivo> libreria`
- **THEN** `docker ps` muestra el contenedor `healthy` y los logs muestran el arranque con las tablas creadas

#### Scenario: Sin DATABASE_URL (D-05)
- **WHEN** se corre la imagen sin `--env-file` ni `DATABASE_URL`
- **THEN** el contenedor termina con código de salida distinto de 0 indicando que falta `DATABASE_URL`

### Requirement: Despliegue accesible y persistente en el VPS
La aplicación SHALL quedar accesible desde afuera del VPS en la URL declarada en `DEPLOY.md`, con los datos en la base del servidor y no en el contenedor, de modo que recrear el contenedor no los pierda.

#### Scenario: Acceso desde afuera (D-03)
- **WHEN** desde fuera del VPS se piden `GET /health/ready`, `GET /libros/` y la venta del caso C-06 en la URL pública
- **THEN** responden 200, 200 con la lista de libros y 201 con total `77000.00`

#### Scenario: Recrear el contenedor (D-04)
- **WHEN** se ejecuta `docker rm -f libreria` y el mismo `docker run`
- **THEN** el contenedor vuelve a estar `healthy` y `GET /ventas/` sigue devolviendo las ventas previas

#### Scenario: Aviso en los logs del contenedor (D-07)
- **WHEN** se revisa `docker logs libreria` después de la venta de D-03
- **THEN** la línea del comprobante aparece después de la línea `POST /ventas/ ... 201`

### Requirement: Documentación de entrega
El repositorio SHALL incluir `README.md` (integrantes y pasos para levantar el proyecto desde cero), `DEPLOY.md` (URL pública, día y hora del despliegue, comandos `docker build` y `docker run` completos con el nombre del archivo de variables y sin su contenido, cambios hechos para el contenedor y cómo se actualiza) y `evidencia/` con la salida de C-07 y de cada caso D.

#### Scenario: DEPLOY.md completo
- **WHEN** se revisa `DEPLOY.md` después del despliegue
- **THEN** no quedan marcadores `[COMPLETAR]` y cada caso D tiene su archivo en `evidencia/`
