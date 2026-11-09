"""Traducción de errores de la base a respuestas HTTP con mensaje propio (RN-12).

Cada service declara qué mensaje corresponde a cada restricción; acá está la
mecánica común. Nunca se devuelve al cliente el texto de la base.
"""

import logging

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

logger = logging.getLogger("libreria.errores")

MENSAJE_GENERICO = "La operación no se pudo registrar porque no cumple una regla de los datos."


def nombre_de_restriccion(error: IntegrityError) -> str | None:
    """Devuelve el nombre de la restricción que rechazó la escritura.

    SQLAlchemy envuelve la excepción de asyncpg: el nombre está en la excepción
    original o en su causa (__cause__).
    """
    original = error.orig
    for candidato in (original, getattr(original, "__cause__", None)):
        nombre = getattr(candidato, "constraint_name", None)
        if nombre:
            return nombre
    return None


def traducir_integridad(
    error: IntegrityError,
    mensajes: dict[str, str],
    codigos: dict[str, int] | None = None,
) -> HTTPException:
    """Convierte un IntegrityError en HTTPException (409, salvo que se indique otro código)."""
    restriccion = nombre_de_restriccion(error) or ""
    logger.info("Escritura rechazada por la restricción %s", restriccion or "(sin nombre)")
    detalle = mensajes.get(restriccion, MENSAJE_GENERICO)
    codigo = (codigos or {}).get(restriccion, status.HTTP_409_CONFLICT)
    return HTTPException(status_code=codigo, detail=detalle)


async def confirmar(
    sesion: AsyncSession,
    mensajes: dict[str, str],
    codigos: dict[str, int] | None = None,
) -> None:
    """Hace commit; si la base rechaza la escritura, deshace y responde con mensaje propio."""
    try:
        await sesion.commit()
    except IntegrityError as error:
        await sesion.rollback()
        raise traducir_integridad(error, mensajes, codigos) from None


def no_encontrado(recurso: str) -> HTTPException:
    """404 con un mensaje propio, por ejemplo: "La editorial no existe."."""
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{recurso} no existe.")
