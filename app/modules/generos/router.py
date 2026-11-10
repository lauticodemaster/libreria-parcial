from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.paginacion import PaginacionDep
from app.modules.generos import service
from app.modules.generos.schemas import GeneroCreate, GeneroRead, LibroDelGenero

router = APIRouter(prefix="/generos", tags=["generos"])

SesionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post(
    "/",
    response_model=GeneroRead,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Ya existe un género con ese nombre"}},
)
async def crear_genero(datos: GeneroCreate, sesion: SesionDep):
    return await service.crear(sesion, datos)


@router.get("/", response_model=list[GeneroRead])
async def listar_generos(pagina: PaginacionDep, sesion: SesionDep):
    return await service.listar(sesion, pagina)


@router.get(
    "/{genero_id}/libros",
    response_model=list[LibroDelGenero],
    responses={404: {"description": "El género no existe"}},
)
async def libros_del_genero(genero_id: int, pagina: PaginacionDep, sesion: SesionDep):
    return await service.libros_de(sesion, genero_id, pagina)
