# Discovery — Librería (API de catálogo y ventas)

**Fecha**: 2026-11-09
**Fuentes investigadas**: la consigna del parcial (`docs/consigna_parcial.pdf`). No hubo scraping de competidores:
el grupo no aportó URLs y el dominio lo define la consigna.
**Cómo se cerró**: el grupo respondió las fuentes, el problema y la situación actual, y delegó el resto de los
puntos y la confirmación final ("decidí todo vos, revisá la consigna"). Lo que se completó por esa delegación
está marcado como **Supuesto**.

## 1. Problema que resuelve

Una librería de barrio necesita una API para administrar su catálogo (editoriales, géneros, autores y libros) y
registrar a sus clientes y sus ventas sin errores de precio ni datos inconsistentes. El grupo, además, necesita
demostrarlo funcionando y desplegado para aprobar el parcial de Programación III (capítulos 1 a 4).

## 2. Usuarios / roles

- **Personal de la librería**: carga el catálogo y registra ventas.
- **Cliente de la librería**: no usa la API; es un dato del sistema y recibe el aviso del comprobante.
- **Cátedra (corrector)**: prueba la API desplegada y los casos C-01 a C-08 y D-01 a D-07.
- **Grupo (operador)**: construye la imagen, la despliega y la mantiene en el VPS.

**Supuesto**: estos cuatro roles los eligió el discovery por delegación del grupo.

## 3. Casos de uso

1. Como personal, quiero dar de alta editoriales, géneros y autores para armar el catálogo.
2. Como personal, quiero dar de alta un libro con su editorial, su género y sus autores (con rol y orden) en un
   solo pedido.
3. Como personal, quiero registrar un cliente con su perfil (teléfono y dirección) una sola vez.
4. Como personal, quiero registrar una venta con sus renglones y que el sistema copie los precios y calcule el total.
5. Como cátedra, quiero probar la API en una URL pública y ver la evidencia de cada caso.

## 4. Competidores / soluciones existentes

| Solución | Problema que resuelve | Pricing | Diferenciadores |
|---|---|---|---|
| Planilla de cálculo o cuaderno | Registro manual de libros y ventas | Gratis | Sin control de precios ni de duplicados; el historial depende de quien lo carga |
| Sistemas de gestión comerciales | Stock, facturación y punto de venta | Pagos, por licencia o abono | Completos pero grandes para una librería chica; no son parte del ejercicio |

**Notas**: la referencia real es la planilla o el cuaderno (respuesta del grupo). El proyecto no compite con un
sistema comercial: resuelve el núcleo (catálogo y ventas consistentes) y demuestra los contenidos de la materia.

## 5. Funcionalidades necesarias

- Los endpoints de referencia de la consigna: salud (`/health/live`, `/health/ready`), CRUD de editoriales,
  géneros y autores, libros con autorías, clientes con perfil uno a uno, ventas con renglones.
- Aviso del comprobante en segundo plano (`BackgroundTasks`) al registrar una venta.
- Lecturas sin N+1 y errores de la base traducidos a mensajes propios.
- Imagen Docker sobre `python:3.12-alpine` desplegada con `docker run --env-file`.

**Supuesto**: el MVP es exactamente lo que pide la consigna, ni más ni menos.

## 6. Funcionalidades opcionales

- Descontar stock al registrar una venta (la consigna no lo pide).
- Autenticación y roles (capítulo 5, fuera de alcance).
- Migraciones de esquema (hoy se usa `create_all`).
- Un frontend web que consuma la API (por ejemplo, el catálogo HTML/CSS/JS del parcial anterior del grupo).

## 7. Reglas de negocio

- RN-01 a RN-12 de la consigna: ISBN y email únicos; precio > 0 y stock ≥ 0; la venta se crea con sus renglones,
  al menos uno y sin libros repetidos; el precio de cada renglón se copia del libro; el total lo calcula el
  servidor; las ventas no se modifican; un perfil por cliente; listados paginados (`limit` 1 a 100, `offset` desde
  0); búsqueda por título con parámetro ligado; ningún error devuelve texto interno de la base.
- Técnicas: la base garantiza unicidad, claves foráneas y comprobaciones (no se consulta antes); sin carga
  perezosa; dinero con `Decimal`.

## 8. Integraciones

- PostgreSQL 16 (en el despliegue, la base del servidor).
- Ninguna integración externa real: el aviso del comprobante es simulado (`await asyncio.sleep(0.5)` y un
  mensaje en el log). No hay pagos ni correo.

## 9. Restricciones

- Stack obligatorio: Python 3.12, FastAPI asincrónico, SQLModel, SQLAlchemy 2 asincrónico, asyncpg, PostgreSQL 16,
  python-dotenv, Docker.
- Nombres de tablas y columnas obligatorios; estructura de carpetas obligatoria por módulo.
- Imagen `python:3.12-alpine`, usuario sin root, sin secretos en el repositorio, la imagen ni el zip; sin Docker
  Compose; esquema con `create_all`, sin migraciones.
- Entrega en un `.zip` por grupo con fecha límite del campus; despliegue en línea hasta que se publiquen las notas.

## 10. Riesgos

- **Supuesto sin probar al inicio**: que la cátedra entregara su VPS a tiempo. Se mitigó desplegando en el
  servidor del grupo (https://libreria.saferazi.me) con una base propia.
- Que las dependencias no instalaran en Alpine (musl). Verificado: todas tienen wheel, la imagen se construye sin
  compilar.
- Que el despliegue dependa de un servidor compartido con otros servicios (EasyPanel): un reinicio de Docker lo
  baja unos segundos; se mitigó con `--restart unless-stopped`.
- Que la evidencia PNG generada a partir de la salida real de la consola no se acepte como "captura".

## 11. Preguntas abiertas

- ¿La cátedra va a entregar su propio VPS y base? Si lo hace, hay que repetir los pasos de `DEPLOY.md` con sus datos.
- ¿Hay que descontar stock al vender?
- ¿Se acepta la evidencia PNG generada desde la salida de consola?
- ¿Se versionan en el zip de entrega la fundación OPSX (`openspec/`, `knowledge-base/`, `discovery/`, `docs/`)?
