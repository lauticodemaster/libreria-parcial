# Evidencia

Salidas de consola (`.txt`) y capturas (`.png`) de los casos del parcial. Cada captura muestra sólo la
salida de la consola del archivo `.txt` del mismo nombre.

## Generada en la máquina del grupo (08/11/2026)

Windows 11, Python 3.12.10, PostgreSQL 16.2 local y servidor uvicorn en `http://localhost:8000`.
En esa máquina no había Docker: esta parte es de la aplicación corriendo directamente con uvicorn. Los casos D
se hicieron después en el VPS (sección siguiente).

| Archivo | Qué muestra |
|---|---|
| `C-01_a_C-08_pedidos_y_respuestas.txt` / `.png` | Los pedidos de `test/casos_minimos.http`, en orden después de `python -m app.seed`, con el código y el cuerpo de cada respuesta y el esperado |
| `C-01_a_C-08_consola_del_servidor.txt` | La consola del servidor (`SQL_ECHO=true`) durante esos pedidos. El aviso del comprobante de C-06 aparece al final, después de otras respuestas: el aviso no bloquea al servidor |
| `C-07_consultas_detalle_libro_y_venta.txt` / `.png` | **Caso C-07**: las consultas del detalle de un libro (1 y 3 autores) y de una venta (1 y 2 renglones). Siempre 2 |
| `arranque_con_base_vacia_create_all.txt` / `.png` | El arranque sobre una base vacía: `create_all` crea las 9 tablas y los índices |
| `reinicio_sin_recrear_tablas.txt` / `.png` | Equivalente local de D-04: al reiniciar no se recrea nada y los datos siguen |
| `arranque_sin_database_url.txt` / `.png` | Equivalente local de D-05: sin `DATABASE_URL`, o con la base caída, el proceso termina con error |
| `esquema_postgresql.txt` | El esquema real que dejó `create_all`: UNIQUE, CHECK, claves foráneas e índices |
| `pruebas_automaticas_pytest.txt` / `.png` | 106 pruebas automáticas contra PostgreSQL 16 real, todas aprobadas: 83 de la API y 23 comprobaciones estáticas del Dockerfile y del `.dockerignore` (regenerado el 09/11/2026) |
| `dependencias_alpine_sin_compilar.txt` | Todas las dependencias tienen wheel para Alpine (musllinux): la imagen se construye sin compilador |

## Casos D en el VPS (servidor saferazi, 08/11/2026)

La cátedra todavía no entregó su VPS: el proyecto se desplegó en el servidor del grupo, con una base PostgreSQL 16
propia, y queda en línea en **https://libreria.saferazi.me**. Comandos completos en `DEPLOY.md`. En ningún archivo
aparece la contraseña de la base: vive sólo en el archivo de variables del servidor.

| Archivo | Qué muestra |
|---|---|
| `D-01_docker_images.txt` / `.png` | `python:3.12-alpine` ocupa 74.8 MB en disco (< 100 MB) y el Dockerfile parte de ella; `libreria:latest` 250 MB |
| `D-02_build_run_ps_logs.txt` / `_parte1.png` (build) / `_parte2.png` (run) | Build en el servidor sin compilar nada; `docker ps` con `healthy`; `docker logs` con el arranque completo y las tablas creadas |
| `datos_iniciales_en_el_contenedor.txt` / `.png` | `docker exec libreria python -m app.seed` |
| `D-03_desde_afuera.txt` / `.png` | Desde la PC del grupo, en la URL pública: 200, 200 con los libros y 201 con los precios copiados y total `77000.00` |
| `D-04_recrear_contenedor.txt` / `.png` | `docker rm -f` y el mismo `docker run`: vuelve a `healthy` y los datos siguen |
| `D-05_sin_database_url.txt` / `.png` | Sin `DATABASE_URL`, el contenedor termina con código 3 |
| `D-06_usuario.txt` / `.png` | `docker exec libreria id`: `uid=100(libreria)`, no es root |
| `D-07_aviso_en_logs.txt` / `.png` | El aviso del comprobante aparece en `docker logs` después de la línea `POST /ventas/ ... 201` |
