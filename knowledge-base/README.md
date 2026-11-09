# Librería — Base de Conocimiento

Base de conocimiento generada a partir de la consigna del parcial de Programación III (capítulos 1 a 4,
`docs/consigna_parcial.pdf`) y del código del proyecto. El Discovery de la fundación está en
`discovery/discovery.md` (problema, usuarios, casos de uso, reglas, restricciones, riesgos y preguntas abiertas).

## Índice de Archivos

| Archivo | Contenido |
|---|---|
| [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito, objetivos por actor, alcance y fuera de alcance |
| [02_descripcion_general.md](02_descripcion_general.md) | Stack con versiones, arquitectura, endpoints |
| [03_actores_y_roles.md](03_actores_y_roles.md) | Actores; sin RBAC (autenticación fuera de alcance) |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | Tablas obligatorias, restricciones, índices, relaciones y datos iniciales |
| [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | RN-01 a RN-12 de la consigna y reglas técnicas RT-* |
| [06_funcionalidades.md](06_funcionalidades.md) | Épicas e historias alineadas con el reparto y los changes |
| [07_flujos_principales.md](07_flujos_principales.md) | Arranque, alta de libro, venta, despliegue |
| [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones, directorios, seguridad, variables de entorno |
| [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | DD-01 a DD-09 y supuestos |
| [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | Inconsistencias y preguntas pendientes |
| [11_contenedor_y_despliegue.md](11_contenedor_y_despliegue.md) | Dockerfile, ejecución y casos D |

## Quick Start para Desarrolladores

1. Entender el dominio → [01](01_vision_y_objetivos.md), [03](03_actores_y_roles.md)
2. Entender los datos → [04](04_modelo_de_datos.md)
3. Entender las reglas → [05](05_reglas_de_negocio.md)
4. Entender la arquitectura → [02](02_descripcion_general.md), [08](08_arquitectura_propuesta.md)
5. Implementar → [07](07_flujos_principales.md), [06](06_funcionalidades.md)
6. Antes de codificar → [10](10_preguntas_abiertas.md)

## Resumen Ejecutivo

API FastAPI asincrónica con SQLModel y PostgreSQL 16 para el catálogo y las ventas de una librería, con
todas las relaciones del capítulo 4 (agregación, muchos a muchos con datos, uno a uno, asociación y
composición), lecturas sin N+1 y errores de la base traducidos a mensajes propios. Se empaqueta en una
imagen `python:3.12-alpine` sin root y se despliega en el VPS con `docker run --env-file`.
