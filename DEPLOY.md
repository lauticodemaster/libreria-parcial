# Despliegue en el VPS

Grupo **Saferazi**. La cátedra no entregó todavía los datos de su VPS, así que el proyecto se desplegó en el
servidor del grupo (**saferazi**), con una base PostgreSQL 16 propia en lugar de la del servidor de la cátedra.
Si la cátedra entrega su VPS, se repiten los mismos pasos cambiando sólo el archivo de variables (la dirección de
su base) y el puerto.

## Datos del despliegue

| Dato | Valor |
|---|---|
| URL pública | **https://libreria.saferazi.me** (por ejemplo, <https://libreria.saferazi.me/health/ready> y <https://libreria.saferazi.me/docs>) |
| Día y hora del despliegue | **08/11/2026, 23:42** (hora de Argentina, UTC-3) |
| Servidor | saferazi: Ubuntu 26.04, Docker 29.7.2, detrás de Traefik y de un túnel de Cloudflare |
| Dónde se construyó la imagen | En el propio servidor, a partir del proyecto copiado a `/home/saferazi/libreria/app` |
| Archivo de variables de la aplicación | `/home/saferazi/libreria/libreria.env` (permisos 600; fuera del repositorio y de la imagen) |
| Archivo de variables de la base | `/home/saferazi/libreria/libreria-db.env` (permisos 600) |
| Base de datos | Contenedor `libreria-db` (`postgres:16-alpine`), volumen `libreria-db-data`, red `libreria-net`, **sin puertos publicados** |
| Puerto | La aplicación publica el `8000` del contenedor sólo en `127.0.0.1:8090` del servidor |

## 1. Archivos de variables (sólo en el servidor)

Los dos archivos se crearon en el servidor con permisos 600. La contraseña de la base se generó ahí mismo con
`openssl rand` y no aparece en el repositorio, en la imagen, en la evidencia ni en este documento. Tienen esta
forma (sin los valores):

```env
# /home/saferazi/libreria/libreria.env  (lo usa la aplicación)
DATABASE_URL=postgresql+asyncpg://libreria:<contraseña>@libreria-db:5432/libreria
SQL_ECHO=false
```

```env
# /home/saferazi/libreria/libreria-db.env  (lo usa el contenedor de PostgreSQL)
POSTGRES_USER=libreria
POSTGRES_PASSWORD=<contraseña>
POSTGRES_DB=libreria
```

La base no está en `localhost`: dentro del contenedor, `localhost` es el propio contenedor. La aplicación llega
a la base por el nombre `libreria-db`, porque los dos contenedores comparten la red `libreria-net`.

## 2. La base de datos

```bash
docker network create libreria-net
docker volume create libreria-db-data
docker run -d --name libreria-db --network libreria-net --restart unless-stopped \
  --env-file /home/saferazi/libreria/libreria-db.env \
  -v libreria-db-data:/var/lib/postgresql/data postgres:16-alpine
```

## 3. Construir la imagen

```bash
cd /home/saferazi/libreria/app
docker build -t libreria .
```

## 4. Correr el contenedor

```bash
docker run -d --name libreria -p 127.0.0.1:8090:8000 --restart unless-stopped \
  --network libreria-net --env-file /home/saferazi/libreria/libreria.env libreria
docker network connect easypanel libreria
```

- `-p 127.0.0.1:8090:8000` publica la aplicación sólo en la interfaz local del servidor. Docker se salta UFW, así
  que publicar en `0.0.0.0` dejaría el puerto abierto a la red; lo público entra por Traefik.
- `--restart unless-stopped` la vuelve a levantar si termina, si se reinicia el servidor o si Docker se reinicia.
- `--network libreria-net` la conecta con la base; `docker network connect easypanel` la conecta con la red de
  Traefik, que es quien la publica.

Comprobar que quedó sana y cargar los datos iniciales:

```bash
docker ps
docker logs libreria
docker exec libreria wget -qO- http://127.0.0.1:8000/health/live
docker exec libreria python -m app.seed
```

## 5. Publicación en https://libreria.saferazi.me

El túnel de Cloudflare ya manda todo `*.saferazi.me` a Traefik. Traefik (administrado por EasyPanel) lee **todos**
los archivos de `/etc/easypanel/traefik/config/` y vigila los cambios (`TRAEFIK_PROVIDERS_FILE_DIRECTORY` y
`TRAEFIK_PROVIDERS_FILE_WATCH`). EasyPanel regenera sólo `main.yaml`, así que se agregó un archivo propio al lado,
sin tocar los de EasyPanel:

- `/etc/easypanel/traefik/config/libreria.yaml`: dos routers para `Host(libreria.saferazi.me)` (http con
  redirección a https y https con certificado de Let's Encrypt) y el servicio `http://libreria:8000`.
- Respaldo: `/home/saferazi/libreria/traefik-libreria.yaml`.

Para dar de baja la publicación alcanza con borrar ese archivo; Traefik lo nota solo.

## 6. Cómo se actualiza la aplicación

Se copia el proyecto nuevo, se construye la imagen de nuevo, se elimina el contenedor y se lo vuelve a correr con
el mismo comando. Los datos no se pierden: viven en el volumen de la base, no en el contenedor de la aplicación, y
`create_all` sólo crea las tablas que faltan (verificado en D-04).

```bash
cd /home/saferazi/libreria/app      # copiar acá el proyecto nuevo, sin .venv, .env ni __pycache__
docker build -t libreria .
docker rm -f libreria
docker run -d --name libreria -p 127.0.0.1:8090:8000 --restart unless-stopped \
  --network libreria-net --env-file /home/saferazi/libreria/libreria.env libreria
docker network connect easypanel libreria
```

## 7. Cambios hechos al proyecto para que corra en el contenedor

**Ninguno en la aplicación.** Arrancó en el contenedor tal como estaba: el `HEALTHCHECK` ya usaba `127.0.0.1` (no
`localhost`), uvicorn ya escuchaba en `0.0.0.0` y las dependencias se instalaron sin compilar nada. Lo único que
se ajustó fue el `.dockerignore`, para dejar afuera los artefactos de OPSX y de la base de conocimiento: el contexto
que se envía al construir pesa 66 KB.

Diferencias con el comando de ejemplo de la consigna, por usar el servidor del grupo:

- `--network libreria-net` y `docker network connect easypanel`: la base es un contenedor propio y la publicación
  la hace Traefik.
- `-p 127.0.0.1:8090:8000` en lugar de `-p <puerto>:8000`, por la razón de la sección 4.
- No hace falta `--add-host=host.docker.internal:host-gateway`, porque la base no corre en el host.

Durante el despliegue, a las 23:49, una actualización de paquetes del sistema hecha desde otra sesión del servidor
reinició el servicio de Docker. Los dos contenedores volvieron solos gracias a `--restart unless-stopped` y la base
no perdió datos; en `evidencia/D-07_aviso_en_logs.txt` se ve el apagado y el arranque de la aplicación.

## 8. Casos D

| Caso | Resultado | Evidencia |
|---|---|---|
| D-01 | `python:3.12-alpine` ocupa 74.8 MB en disco (< 100 MB); `libreria:latest` 250 MB; el Dockerfile parte de la base | `D-01_docker_images.txt` / `.png` |
| D-02 | Build sin compilar nada; `docker ps`: `Up 45 seconds (healthy)`; en `docker logs`, el arranque completo con las tablas creadas; `\dt` muestra las 9 tablas | `D-02_build_run_ps_logs.txt` / `_parte1.png` / `_parte2.png` |
| D-03 | Desde la PC del grupo: `/health/ready` 200, `/libros/` 200 con los 6 libros, `POST /ventas/` 201 con id 2, precios copiados y total `77000.00` | `D-03_desde_afuera.txt` / `.png` |
| D-04 | `docker rm -f` + el mismo `docker run`: vuelve a `healthy` y las ventas 1 y 2 siguen | `D-04_recrear_contenedor.txt` / `.png` |
| D-05 | Sin `DATABASE_URL`: `RuntimeError` con mensaje propio, `estado=exited código de salida=3` | `D-05_sin_database_url.txt` / `.png` |
| D-06 | `docker exec libreria id`: `uid=100(libreria)`; no es root | `D-06_usuario.txt` / `.png` |
| D-07 | En `docker logs`, el aviso del comprobante de la venta 2 aparece justo después de `POST /ventas/ ... 201 Created` | `D-07_aviso_en_logs.txt` / `.png` |

Los datos iniciales se cargaron con `docker exec libreria python -m app.seed`
(`evidencia/datos_iniciales_en_el_contenedor.txt` / `.png`).

El contenedor queda corriendo hasta que se publiquen las notas.
