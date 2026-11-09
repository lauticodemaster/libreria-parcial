# Actores y Roles

## Actores del sistema

| Actor | Descripción | Cómo interactúa |
|---|---|---|
| Personal de la librería | Quien carga el catálogo y registra ventas | Cliente HTTP contra la API (REST Client, curl, `/docs`) |
| Cliente de la librería | Persona que compra; es un **dato** del sistema, no un usuario autenticado | No interactúa: recibe el aviso simulado del comprobante |
| Operador del despliegue (grupo) | Construye la imagen y corre el contenedor en el VPS | `docker build`, `docker run`, `docker exec libreria python -m app.seed` |
| Corrector de la cátedra | Prueba el proyecto desplegado | Pedidos HTTP desde afuera del VPS y lectura de `DEPLOY.md` y `evidencia/` |
| Proceso de fondo | Aviso del comprobante | `BackgroundTasks` después de responder el alta de venta |

## RBAC — Matriz de permisos

La consigna deja la autenticación y la autorización **fuera de alcance** (capítulo 5). No hay roles:
todo consumidor de la API tiene los mismos permisos.

| Rol | Recurso | Permisos |
|---|---|---|
| (sin autenticación) | Editoriales, géneros, autores, libros, clientes | Crear, leer, modificar parcialmente |
| (sin autenticación) | Ventas | Crear y leer. **Nunca** modificar ni borrar (RN-08) |
| (sin autenticación) | Salud | Leer |

## Rutas públicas

Todas. En el despliegue sólo se publica el puerto de la aplicación (`-p <puerto>:8000`); la base no se
expone.
