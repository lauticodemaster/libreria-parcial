# Persona 4: Danilo Serrano — qué te toca y cómo subirlo

Grupo **Saferazi**. Persona 4: **Danilo Serrano**.

**Orden:** **Cuarta y última**, después del push de Persona 3. El orden es Lautaro → Daniela → Jesús → Danilo.

## Qué te toca

- El módulo **`ventas`**: alta con sus renglones (`RenglonVenta`, composición), precio copiado del libro, total calculado por el servidor y aviso del comprobante con `BackgroundTasks`.
- Los datos iniciales (`app/seed.py`), los casos C-01 a C-08 (`test/casos_minimos.http`) y sus pruebas (`tests/test_ventas.py`, `tests/test_datos_iniciales.py`).
- La imagen: `Dockerfile` y `.dockerignore` (que también deja afuera los artefactos OPSX y la KB), con sus pruebas estáticas (`tests/test_contenedor.py`). La documentación: `README.md` y `DEPLOY.md`. La carpeta `evidencia/`.
- Tu change OPSX archivado (`openspec/changes/archive/2026-11-08-ventas-docker-despliegue/`) y las specs `openspec/specs/ventas/` y `openspec/specs/contenedor-y-despliegue/`, con sus 22 tareas completas (incluidos el despliegue y los casos D).
- El despliegue: el proyecto quedó en línea en https://libreria.saferazi.me (servidor del grupo, con base PostgreSQL 16 propia). `DEPLOY.md` tiene los comandos reales y `evidencia/` los casos D-01 a D-07. El `README.md` ya tiene los nombres de los cuatro integrantes.

## Tus archivos (54)

Están en esta carpeta con la misma ruta que tienen en el repositorio. Nadie más toca estos archivos y vos no tocás los de los demás.

- `app/modules/ventas/schemas.py`
- `app/modules/ventas/service.py`
- `app/modules/ventas/router.py`
- `app/seed.py`
- `tests/test_ventas.py`
- `tests/test_datos_iniciales.py`
- `tests/test_contenedor.py`
- `test/casos_minimos.http`
- `Dockerfile`
- `.dockerignore`
- `README.md`
- `DEPLOY.md`
- `openspec/changes/archive/2026-11-08-ventas-docker-despliegue/.openspec.yaml`
- `openspec/changes/archive/2026-11-08-ventas-docker-despliegue/design.md`
- `openspec/changes/archive/2026-11-08-ventas-docker-despliegue/proposal.md`
- `openspec/changes/archive/2026-11-08-ventas-docker-despliegue/specs/contenedor-y-despliegue/spec.md`
- `openspec/changes/archive/2026-11-08-ventas-docker-despliegue/specs/ventas/spec.md`
- `openspec/changes/archive/2026-11-08-ventas-docker-despliegue/tasks.md`
- `openspec/specs/contenedor-y-despliegue/spec.md`
- `openspec/specs/ventas/spec.md`
- `evidencia/C-01_a_C-08_consola_del_servidor.txt`
- `evidencia/C-01_a_C-08_pedidos_y_respuestas.txt`
- `evidencia/C-01_a_C-08_pedidos_y_respuestas_parte1.png`
- `evidencia/C-01_a_C-08_pedidos_y_respuestas_parte2.png`
- `evidencia/C-07_consultas_detalle_libro_y_venta.png`
- `evidencia/C-07_consultas_detalle_libro_y_venta.txt`
- `evidencia/D-01_docker_images.png`
- `evidencia/D-01_docker_images.txt`
- `evidencia/D-02_build_run_ps_logs.txt`
- `evidencia/D-02_build_run_ps_logs_parte1.png`
- `evidencia/D-02_build_run_ps_logs_parte2.png`
- `evidencia/D-03_desde_afuera.png`
- `evidencia/D-03_desde_afuera.txt`
- `evidencia/D-04_recrear_contenedor.png`
- `evidencia/D-04_recrear_contenedor.txt`
- `evidencia/D-05_sin_database_url.png`
- `evidencia/D-05_sin_database_url.txt`
- `evidencia/D-06_usuario.png`
- `evidencia/D-06_usuario.txt`
- `evidencia/D-07_aviso_en_logs.png`
- `evidencia/D-07_aviso_en_logs.txt`
- `evidencia/README.md`
- `evidencia/arranque_con_base_vacia_create_all.png`
- `evidencia/arranque_con_base_vacia_create_all.txt`
- `evidencia/arranque_sin_database_url.png`
- `evidencia/arranque_sin_database_url.txt`
- `evidencia/datos_iniciales_en_el_contenedor.png`
- `evidencia/datos_iniciales_en_el_contenedor.txt`
- `evidencia/dependencias_alpine_sin_compilar.txt`
- `evidencia/esquema_postgresql.txt`
- `evidencia/pruebas_automaticas_pytest.png`
- `evidencia/pruebas_automaticas_pytest.txt`
- `evidencia/reinicio_sin_recrear_tablas.png`
- `evidencia/reinicio_sin_recrear_tablas.txt`

## 1. Preparar la carpeta del repositorio

Esperá a que **Jesús (Persona 3)** avise que hizo push. Después:

Si todavía no clonaste el repositorio:

```bash
git clone https://github.com/lauticodemaster/libreria-parcial.git
cd libreria-parcial
```

Si ya lo tenías clonado, traé lo último:

```bash
cd libreria-parcial
git pull
```

Si es la primera vez que usás git en esta computadora:

```bash
git config --global user.name "Tu Nombre y Apellido"
git config --global user.email "el-mail-de-tu-cuenta@github"
```

## 2. Copiar tus archivos al repositorio

Desde la carpeta `libreria-parcial`, copiá el contenido de esta carpeta (`4 - Danilo Serrano`, la que sale de descomprimir `4 - Danilo Serrano.zip`) **menos este `COMMIT.md`**. Los comandos suponen que la descomprimiste en Descargas; si está en otro lado, ajustá la ruta.

En PowerShell (Windows):

```powershell
robocopy "$HOME\Downloads\4 - Danilo Serrano" . /E /XF COMMIT.md
```

En Git Bash, Linux o macOS:

```bash
cp -r ~/Downloads/"4 - Danilo Serrano"/. .
rm COMMIT.md
```

## 3. Commit y push

Revisá que sólo aparezcan tus archivos y que **no** aparezca ningún `.env`, `.venv` ni `__pycache__`:

```bash
git status
```

Agregá exactamente tus archivos (es un solo comando, en una línea):

```bash
git add app/modules/ventas/schemas.py app/modules/ventas/service.py app/modules/ventas/router.py app/seed.py tests/test_ventas.py tests/test_datos_iniciales.py tests/test_contenedor.py test/casos_minimos.http Dockerfile .dockerignore README.md DEPLOY.md openspec/changes/archive/2026-11-08-ventas-docker-despliegue/.openspec.yaml openspec/changes/archive/2026-11-08-ventas-docker-despliegue/design.md openspec/changes/archive/2026-11-08-ventas-docker-despliegue/proposal.md openspec/changes/archive/2026-11-08-ventas-docker-despliegue/specs/contenedor-y-despliegue/spec.md openspec/changes/archive/2026-11-08-ventas-docker-despliegue/specs/ventas/spec.md openspec/changes/archive/2026-11-08-ventas-docker-despliegue/tasks.md openspec/specs/contenedor-y-despliegue/spec.md openspec/specs/ventas/spec.md evidencia/C-01_a_C-08_consola_del_servidor.txt evidencia/C-01_a_C-08_pedidos_y_respuestas.txt evidencia/C-01_a_C-08_pedidos_y_respuestas_parte1.png evidencia/C-01_a_C-08_pedidos_y_respuestas_parte2.png evidencia/C-07_consultas_detalle_libro_y_venta.png evidencia/C-07_consultas_detalle_libro_y_venta.txt evidencia/D-01_docker_images.png evidencia/D-01_docker_images.txt evidencia/D-02_build_run_ps_logs.txt evidencia/D-02_build_run_ps_logs_parte1.png evidencia/D-02_build_run_ps_logs_parte2.png evidencia/D-03_desde_afuera.png evidencia/D-03_desde_afuera.txt evidencia/D-04_recrear_contenedor.png evidencia/D-04_recrear_contenedor.txt evidencia/D-05_sin_database_url.png evidencia/D-05_sin_database_url.txt evidencia/D-06_usuario.png evidencia/D-06_usuario.txt evidencia/D-07_aviso_en_logs.png evidencia/D-07_aviso_en_logs.txt evidencia/README.md evidencia/arranque_con_base_vacia_create_all.png evidencia/arranque_con_base_vacia_create_all.txt evidencia/arranque_sin_database_url.png evidencia/arranque_sin_database_url.txt evidencia/datos_iniciales_en_el_contenedor.png evidencia/datos_iniciales_en_el_contenedor.txt evidencia/dependencias_alpine_sin_compilar.txt evidencia/esquema_postgresql.txt evidencia/pruebas_automaticas_pytest.png evidencia/pruebas_automaticas_pytest.txt evidencia/reinicio_sin_recrear_tablas.png evidencia/reinicio_sin_recrear_tablas.txt
```

```bash
git commit -m "Módulo ventas con renglones y aviso en segundo plano, datos iniciales, Docker, documentación, evidencia y change OPSX"
```

```bash
git push
```

Si `git push` se rechaza porque hay cambios nuevos, hacé `git pull` y repetí el push.

## 4. Comprobar que arranca (opcional, recomendado)

Con PostgreSQL 16 andando y el `.env` armado como dice el README (`python -m venv .venv`, `pip install -r requirements-dev.txt`, copiar `env.example` como `.env`):

```bash
uvicorn app.main:app --reload
```

Para las pruebas automáticas, con una base de prueba vacía en `TEST_DATABASE_URL` (ver README):

```bash
pytest
```

Resultado esperado después de tu commit: 106 pruebas aprobadas (83 de la API + 23 estáticas del contenedor); aparecen los 7 módulos en `/docs`, `test/casos_minimos.http` da los resultados esperados y `openspec list` no muestra changes activos.

## 5. Armar el .zip de la entrega

La entrega es `Parcial_Cap1a4_Saferazi.zip`, y la sube un solo integrante al campus. `git archive` toma sólo lo que está en el repositorio (sin `.venv`, `__pycache__` ni `.env`), con el proyecto en una sola carpeta. `openspec/` y `knowledge-base/` van incluidos:

```bash
git archive --format=zip --prefix=Parcial_Cap1a4_Saferazi/ -o Parcial_Cap1a4_Saferazi.zip HEAD
```

Ya hay una copia armada en la carpeta `Parcial` del escritorio: `Parcial_Cap1a4_Saferazi.zip`.
