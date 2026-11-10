from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.paginacion import PaginacionDep
from app.modules.editoriales import service
from app.modules.editoriales.schemas import (
    EditorialCreate,
    EditorialRead,
    EditorialUpdate,
    LibroDeEditorial,
)

router = APIRouter(prefix="/editoriales", tags=["editoriales"])

SesionDep = Annotated[AsyncSession, Depends(get_session)]
NO_EXISTE = {404: {"description": "La editorial no existe"}}
CONFLICTO = {409: {"description": "Ya existe una editorial con ese nombre"}}


@router.post("/", response_model=EditorialRead, status_code=status.HTTP_201_CREATED, responses=CONFLICTO)
async def crear_editorial(datos: EditorialCreate, sesion: SesionDep):
    return await service.crear(sesion, datos)


@router.get("/", response_model=list[EditorialRead])
async def listar_editoriales(pagina: PaginacionDep, sesion: SesionDep):
    return await service.listar(sesion, pagina)


@router.get("/{editorial_id}", response_model=EditorialRead, responses=NO_EXISTE)
async def obtener_editorial(editorial_id: int, sesion: SesionDep):
    return await service.obtener(sesion, editorial_id)


@router.patch("/{editorial_id}", response_model=EditorialRead, responses={**NO_EXISTE, **CONFLICTO})
async def actualizar_editorial(editorial_id: int, datos: EditorialUpdate, sesion: SesionDep):
    return await service.actualizar(sesion, editorial_id, datos)


@router.get("/{editorial_id}/libros", response_model=list[LibroDeEditorial], responses=NO_EXISTE)
async def libros_de_la_editorial(editorial_id: int, pagina: PaginacionDep, sesion: SesionDep):
    return await service.libros_de(sesion, editorial_id, pagina)
