"""Paginación común a todos los listados (RN-10).

limit va de 1 a 100 (20 por defecto) y offset arranca en 0. Las restricciones
están declaradas en Query: si no se cumplen, FastAPI responde 422 sin ejecutar
el handler.
"""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query


@dataclass(frozen=True)
class Paginacion:
    limit: int
    offset: int


async def paginacion(
    limit: Annotated[int, Query(ge=1, le=100, description="Cantidad de elementos (1 a 100)")] = 20,
    offset: Annotated[int, Query(ge=0, description="Elementos a saltear (desde 0)")] = 0,
) -> Paginacion:
    return Paginacion(limit=limit, offset=offset)


PaginacionDep = Annotated[Paginacion, Depends(paginacion)]
