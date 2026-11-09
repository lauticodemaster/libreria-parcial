# Visión y Objetivos

## Propósito del sistema

Una API para que una librería de barrio administre su catálogo y registre sus ventas.

La librería vende libros de distintas editoriales, clasificados por género y escritos por uno o varios
autores (que figuran como autor, coautor, traductor o ilustrador). Registra a sus clientes, que pueden
cargar un perfil con teléfono y dirección, y registra cada venta con sus renglones: qué libro, cuántos
ejemplares y a qué precio. El proyecto es el **parcial de Programación III** (capítulos 1 a 4) e integra
FastAPI asincrónico, contratos y CRUD, persistencia relacional con SQLModel y PostgreSQL, y el
despliegue de una imagen de Docker en el VPS de la cátedra.

## Objetivos por actor

| Actor | Objetivo principal | Objetivos secundarios |
|---|---|---|
| Personal de la librería (cliente de la API) | Cargar y consultar el catálogo | Buscar libros por título y género; ver los libros de una editorial, un género o un autor |
| Personal de la librería | Registrar ventas | Que el precio y el total los ponga el servidor; consultar las ventas de un cliente |
| Cliente de la librería (dato, no usuario) | Quedar registrado con su perfil | Recibir el aviso del comprobante de cada compra |
| Grupo de estudiantes | Aprobar el parcial | Demostrar relaciones, carga anticipada, asincronía, imagen de Docker y despliegue |
| Cátedra (corrector) | Probar el proyecto en línea | Correr los casos C-01 a C-08 y D-01 a D-07 |

## Alcance v1.0

- CRUD de editoriales, géneros, autores, libros y clientes, con DTO separados de los modelos de tabla.
- Alta de libro con los ids de editorial, género y autores, más el rol y el orden de cada autoría.
- Perfil de cliente uno a uno.
- Alta de venta con sus renglones en un solo cuerpo, precio copiado del libro y total calculado.
- Aviso del comprobante en segundo plano (`BackgroundTasks`, simulado con `asyncio.sleep(0.5)`).
- Listados paginados y búsqueda de libros por título con parámetro ligado.
- Rutas de salud `/health/live` y `/health/ready`.
- Imagen de Docker sobre `python:3.12-alpine`, ejecutada con `docker run` y `--env-file`.
- Despliegue en el VPS con la base de PostgreSQL que ya tiene el servidor.

## Fuera de alcance

- Autenticación y autorización (capítulo 5).
- Repositorios y Unit of Work (capítulo 6).
- Colas de tareas con Redis (capítulos 7 y 8).
- Docker Compose: el despliegue es de una sola imagen.
- Migraciones: el esquema se crea con `create_all` al arrancar.
- Modificar o borrar ventas (RN-08).
- Descontar stock al vender (la consigna no lo pide).

## Métricas de éxito

- Los casos C-01 a C-08 dan el resultado esperado (`test/casos_minimos.http`).
- El detalle de un libro y de una venta usa una cantidad fija de consultas (C-07).
- El contenedor queda `healthy` en el VPS y los casos D-01 a D-07 tienen su evidencia (cumplido el 08/11/2026 en https://libreria.saferazi.me).
- 106 pruebas automáticas aprobadas contra PostgreSQL 16 (83 de la API y 23 comprobaciones estáticas del contenedor).
