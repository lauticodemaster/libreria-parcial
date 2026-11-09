# proyecto-base Specification

## Purpose
Define la base común de la API de la librería: configuración por entorno, ciclo de vida de la conexión a la base, creación del esquema al arrancar, salud del servicio, traducción de errores de integridad y paginación de listados.

## Requirements

### Requirement: Dirección de la base obligatoria
El sistema SHALL leer la dirección de la base de la variable de entorno `DATABASE_URL` (opcionalmente desde un archivo `.env` no versionado) y MUST NOT tener una dirección por defecto. Si la variable falta o está vacía, el arranque MUST fallar con un error que nombre `DATABASE_URL`.

#### Scenario: Arranque sin DATABASE_URL
- **WHEN** la aplicación arranca sin `DATABASE_URL` definida ni archivo `.env`
- **THEN** la lectura de la configuración falla con un error que menciona `DATABASE_URL` y la aplicación no queda atendiendo

#### Scenario: Variable del entorno prioritaria
- **WHEN** `DATABASE_URL` está definida en el entorno y también en `.env`
- **THEN** se usa el valor del entorno

### Requirement: Diagnóstico de consultas configurable
El sistema SHALL leer la variable `SQL_ECHO`; cuando su valor es verdadero (`true`, `1`, entre otros) las consultas emitidas MUST escribirse en la consola, y en cualquier otro caso (incluido vacío o ausente) MUST NOT escribirse.

#### Scenario: SQL_ECHO verdadero
- **WHEN** `SQL_ECHO` vale `true` o `1`
- **THEN** la configuración activa el eco de consultas

#### Scenario: SQL_ECHO falso o vacío
- **WHEN** `SQL_ECHO` vale `false`, está vacía o no está definida
- **THEN** la configuración no activa el eco de consultas

### Requirement: Recursos de base en el ciclo de vida
El sistema SHALL crear el motor asincrónico y la fábrica de sesiones al arrancar la aplicación, guardarlos en el estado de la aplicación y cerrar el motor al apagarla. Cada petición que lo necesite MUST recibir una sesión propia, y los objetos MUST seguir legibles después del commit sin volver a la base.

#### Scenario: Fábrica sin expiración al confirmar
- **WHEN** la aplicación arrancó
- **THEN** el estado de la aplicación tiene el motor y una fábrica de sesiones configurada con `expire_on_commit=False`

#### Scenario: Cierre del motor al apagar
- **WHEN** la aplicación se apaga
- **THEN** el motor se cierra y se registra un mensaje en el log

### Requirement: Creación del esquema al arrancar
Al arrancar, el sistema SHALL crear las tablas que falten con todos los modelos de tabla ya registrados, y MUST NOT alterar las tablas que ya existen.

#### Scenario: Base vacía
- **WHEN** la aplicación arranca contra una base sin tablas
- **THEN** existen las 9 tablas `editorial`, `genero`, `autor`, `libro`, `libro_autor`, `cliente`, `perfil_cliente`, `venta` y `renglon_venta`

#### Scenario: Tablas existentes
- **WHEN** la aplicación arranca contra una base que ya tiene las tablas con datos
- **THEN** las tablas y sus datos quedan como estaban

### Requirement: Salud del proceso
El sistema SHALL exponer `GET /health/live`, que responde 200 con `{"estado": "vivo"}` y MUST NOT ejecutar consultas contra la base.

#### Scenario: Proceso vivo
- **WHEN** se pide `GET /health/live`
- **THEN** la respuesta es 200 `{"estado": "vivo"}` y no se emite ninguna consulta SQL

### Requirement: Disponibilidad de la base
El sistema SHALL exponer `GET /health/ready`, que ejecuta `SELECT 1` contra la base y responde 200 `{"estado": "listo", "base": "ok"}`; si la base no responde MUST responder 503 `{"estado": "no listo", "base": "sin respuesta"}`.

#### Scenario: Base disponible
- **WHEN** se pide `GET /health/ready` con la base disponible
- **THEN** la única consulta emitida es `SELECT 1` y la respuesta es 200 `{"estado": "listo", "base": "ok"}`

#### Scenario: Base caída
- **WHEN** se pide `GET /health/ready` y la base no responde
- **THEN** la respuesta es 503 `{"estado": "no listo", "base": "sin respuesta"}`

### Requirement: Traducción de errores de integridad
Cuando la base rechaza una escritura por una restricción, el sistema SHALL deshacer la transacción y responder con un mensaje propio elegido por el nombre de la restricción (409 por defecto, u otro código indicado, por ejemplo 404 para una clave foránea). El texto de la base o una traza MUST NOT llegar al cliente.

#### Scenario: Restricción con mensaje propio
- **WHEN** una escritura viola `uq_libro_isbn` y el módulo declaró un mensaje para esa restricción
- **THEN** la respuesta es 409 con ese mensaje

#### Scenario: Restricción con otro código
- **WHEN** una escritura viola una clave foránea para la que el módulo declaró el código 404
- **THEN** la respuesta es 404 con el mensaje declarado

#### Scenario: Error de integridad sin traducir
- **WHEN** un `IntegrityError` llega hasta la aplicación sin que ningún módulo lo traduzca
- **THEN** la respuesta es 409 con un mensaje genérico propio, sin el texto de la base

### Requirement: Paginación común de listados
Todo listado SHALL aceptar `limit` (de 1 a 100, por defecto 20) y `offset` (desde 0, por defecto 0). Un valor fuera de rango MUST responder 422 sin ejecutar el handler.

#### Scenario: Valores por defecto
- **WHEN** se pide un listado sin `limit` ni `offset`
- **THEN** se devuelven como máximo 20 elementos desde el primero

#### Scenario: Fuera de rango
- **WHEN** se pide un listado con `limit=0`, `limit=101` u `offset=-1`
- **THEN** la respuesta es 422

### Requirement: Registro tolerante de módulos
El sistema SHALL registrar las rutas de los módulos `health`, `editoriales`, `generos`, `autores`, `libros`, `clientes` y `ventas`; si un módulo todavía no tiene rutas, MUST arrancar igual, omitirlo y avisarlo en el log. Un error de importación dentro de un módulo existente MUST propagarse.

#### Scenario: Módulo ausente
- **WHEN** el módulo `ventas` todavía no tiene archivo de rutas
- **THEN** la aplicación arranca, registra los demás módulos y deja un aviso en el log

#### Scenario: Proyecto completo
- **WHEN** los 7 módulos tienen rutas
- **THEN** se registran todos y no se omite ninguno

### Requirement: Secretos fuera del repositorio
El repositorio SHALL incluir un `env.example` con la forma de `DATABASE_URL`, `SQL_ECHO` y `TEST_DATABASE_URL` sin ningún valor real, y MUST NOT versionar el archivo `.env`.

#### Scenario: Archivo .env ignorado
- **WHEN** existe un `.env` en la raíz del proyecto
- **THEN** git lo ignora y `env.example` sigue versionado

### Requirement: Pruebas contra PostgreSQL real
Las pruebas automáticas SHALL correr contra la base indicada por `TEST_DATABASE_URL`, vaciando las tablas antes de cada prueba; si la variable no está definida, las pruebas MUST saltearse en lugar de usar otra base.

#### Scenario: Sin base de prueba
- **WHEN** se corre `pytest` sin `TEST_DATABASE_URL`
- **THEN** las pruebas se reportan como salteadas

#### Scenario: Con base de prueba
- **WHEN** se corre `pytest` con `TEST_DATABASE_URL` definida
- **THEN** cada prueba empieza con las 9 tablas vacías
