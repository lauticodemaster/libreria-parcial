from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.health import service
from app.modules.health.schemas import EstadoListo, EstadoVivo

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", response_model=EstadoVivo)
async def vivo() -> EstadoVivo:
    """No toca la base: sólo dice que el proceso responde."""
    return EstadoVivo(estado="vivo")


@router.get(
    "/ready",
    response_model=EstadoListo,
    responses={503: {"description": "La base de datos no responde"}},
)
async def listo(sesion: Annotated[AsyncSession, Depends(get_session)]):
    """Ejecuta SELECT 1 contra la base."""
    if await service.base_responde(sesion):
        return EstadoListo(estado="listo", base="ok")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"estado": "no listo", "base": "sin respuesta"},
    )
