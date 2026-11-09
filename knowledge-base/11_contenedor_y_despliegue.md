# Contenedor y Despliegue

Extra de la KB: la consigna dedica dos ejercicios (7 y 8, 25 puntos) a la imagen y al despliegue.

## Requisitos de la imagen (Ejercicio 7)

| Requisito | Cómo se cumple (`Dockerfile`) |
|---|---|
| Base `python:3.12-alpine` (< 100 MB) | `FROM python:3.12-alpine` |
| Dependencias antes del código, con `--no-cache-dir` | `COPY requirements.txt` + `pip install --no-cache-dir` y recién después `COPY app` |
| Sin root | `adduser -S libreria` + `USER libreria` |
| Sin secretos | `.dockerignore` excluye `.env`, `.venv`, `.git`, `__pycache__`; nada de la base en el Dockerfile |
| uvicorn en 0.0.0.0 | `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]` |
| HEALTHCHECK sobre `/health/ready` | `wget -qO- http://127.0.0.1:8000/health/ready` (127.0.0.1, no localhost: wget en Alpine prueba ::1 primero) |
| Falla sin base | Sin `DATABASE_URL` o con la base caída, uvicorn termina con código 3 |

## Ejecución

```bash
docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped \
  --env-file <archivo-de-variables> libreria
```

Dentro del contenedor `localhost` es el contenedor: si la base corre en el VPS se usa
`host.docker.internal` con `--add-host=host.docker.internal:host-gateway`.

## Casos D (Ejercicio 8)

| Caso | Qué se demuestra | Resultado esperado |
|---|---|---|
| D-01 | `docker images` con la base y la del proyecto | `python:3.12-alpine` por debajo de 100 MB y el Dockerfile parte de ella |
| D-02 | Servidor limpio: `docker build`, `docker run`, `docker ps` | `healthy`; en `docker logs`, el arranque completo con las tablas creadas |
| D-03 | Desde afuera: `/health/ready`, `/libros/`, `POST /ventas/` | 200; 200 con libros; 201 con precios copiados y total |
| D-04 | `docker rm -f libreria` y el mismo `docker run` | Vuelve a estar `healthy` y los datos siguen |
| D-05 | Correr la imagen sin `DATABASE_URL` | Termina con error |
| D-06 | `docker exec libreria id` | No es root |
| D-07 | `docker logs libreria` después de D-03 | El aviso aparece después de la línea de la respuesta |

## Estado

Desplegado el 08/11/2026 en el servidor del grupo: **https://libreria.saferazi.me**, con una base PostgreSQL 16 propia
(`libreria-db`). Los 7 casos D se hicieron de verdad y su evidencia está en `evidencia/D-*.txt` / `.png`; los comandos
completos están en `DEPLOY.md`.
