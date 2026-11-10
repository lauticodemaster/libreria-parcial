from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.paginacion import PaginacionDep
from app.modules.libros import service
from app.modules.libros.schemas import LibroCreate, LibroDetalle, LibroListado, LibroUpdate

router = APIRouter(prefix="/libros", tags=["libros"])

SesionDep = Annotated[AsyncSession, Depends(get_session)]
NO_EXISTE = {404: {"description": "El libro no existe"}}
CONFLICTO = {409: {"description": "ISBN repetido, o editorial, género o autor inexistente"}}


@router.post("/", response_model=LibroDetalle, status_code=status.HTTP_201_CREATED, responses=CONFLICTO)
async def crear_libro(datos: LibroCreate, sesion: SesionDep):
    return await service.crear(sesion, datos)


@router.get("/", response_model=list[LibroListado])
async def listar_libros(
    pagina: PaginacionDep,
    sesion: SesionDep,
    titulo: Annotated[
        str | None,
        Query(min_length=1, max_length=200, description="Parte del título, sin distinguir mayúsculas"),
    ] = None,
    genero_id: Annotated[int | None, Query(description="Sólo los libros de este género")] = None,
):
    return await service.listar(sesion, pagina, titulo=titulo, genero_id=genero_id)


@router.get("/{libro_id}", response_model=LibroDetalle, responses=NO_EXISTE)
async def obtener_libro(libro_id: int, sesion: SesionDep):
    return await service.obtener_detalle(sesion, libro_id)


@router.patch("/{libro_id}", response_model=LibroDetalle, responses={**NO_EXISTE, **CONFLICTO})
async def actualizar_libro(libro_id: int, datos: LibroUpdate, sesion: SesionDep):
    return await service.actualizar(sesion, libro_id, datos)
