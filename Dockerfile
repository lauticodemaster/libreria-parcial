# Imagen del parcial "la librería". Base: python:3.12-alpine (menos de 100 MB).
# Se construye con:  docker build -t libreria .
# Se corre con:      docker run -d --name libreria -p <puerto>:8000 --restart unless-stopped \
#                       --env-file <archivo-de-variables> libreria
FROM python:3.12-alpine

# Sin .pyc en la imagen y con la salida sin búfer (los logs aparecen al instante en docker logs).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Primero sólo las dependencias: mientras requirements.txt no cambie, esta
#    capa sale de la caché y un cambio en el código no reinstala todo.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Usuario sin privilegios: si alguien vulnera la aplicación, no es dueño del contenedor.
RUN addgroup -S libreria && adduser -S -G libreria -H -h /app libreria

# 3) Después el código. Ningún secreto: la dirección de la base entra como
#    variable de entorno al correr el contenedor (--env-file), y el .dockerignore
#    deja afuera .env, .venv, .git y los __pycache__.
COPY --chown=libreria:libreria app ./app

USER libreria

EXPOSE 8000

# Sin Compose, la propia imagen dice cuándo está sana. Se usa 127.0.0.1 y no
# localhost: wget en Alpine resuelve localhost primero a ::1 (IPv6) y uvicorn
# escucha sólo en IPv4, así que con localhost el contenedor quedaría unhealthy.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8000/health/ready || exit 1

# 0.0.0.0: dentro del contenedor, 127.0.0.1 sólo se alcanza desde el propio
# contenedor y el puerto publicado nunca respondería.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
