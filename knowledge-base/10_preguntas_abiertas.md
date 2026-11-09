# Preguntas Abiertas

## Inconsistencias detectadas

### IN-01 — Id de la venta del ejemplo de la consigna
**La consigna dice**: la venta de ejemplo responde con `"id": 2`.
**El proyecto hace**: después de `python -m app.seed` sale con id 2, pero si antes se ejecuta el caso C-05
con cliente inexistente sale con id 3: la inserción rechazada consume un número de la secuencia.
**Impacto**: ninguno funcional. **Resolución**: documentado en `test/casos_minimos.http`.

### IN-02 — Códigos de `POST /autores/`
**La consigna dice**: 201, 422 (sin 409). **El proyecto hace**: igual; `autor` no tiene UNIQUE. Si alguna
vez se agrega una restricción, `confirmar()` ya devuelve 409 con mensaje genérico.

## Preguntas abiertas (priorizadas)

| Prioridad | Pregunta | Bloquea | Decisor |
|---|---|---|---|
| Resuelta | Datos de acceso al VPS: se desplegó en el servidor del grupo (https://libreria.saferazi.me) con base propia; si la cátedra entrega su VPS, se repiten los pasos de `DEPLOY.md` | — | Grupo |
| Resuelta | Nombres de los integrantes: Grupo Saferazi (ver `README.md`) | — | Grupo |
| Media | ¿Hay que descontar stock al registrar una venta? (SU-01) | Ninguno (fuera de la consigna) | Cátedra |
| Baja | ¿Se acepta que la evidencia PNG sea una imagen generada a partir de la salida real de la consola? | Entrega | Cátedra |
| Baja | ¿Se versiona la carpeta `openspec/` y la KB en el zip de entrega? | Entrega | Grupo |
