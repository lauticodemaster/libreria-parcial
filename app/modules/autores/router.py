from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.paginacion import PaginacionDep
from app.modules.autores import service
from app.modules.autores.schemas import AutorCreate, AutorRead, AutorUpdate, LibroDelAutor

router = APIRouter(prefix="/autores", tags=["autores"])

SesionDep = Annotated[AsyncSession, Depends(get_session)]
NO_EXISTE = {404: {"description": "El autor no existe"}}


@router.post("/", response_model=AutorRead, status_code=status.HTTP_201_CREATED)
async def crear_autor(datos: AutorCreate, sesion: SesionDep):
    return await service.crear(sesion, datos)


@router.get("/", response_model=list[AutorRead])
async def listar_autores(pagina: PaginacionDep, sesion: SesionDep):
    return await service.listar(sesion, pagina)


@router.get("/{autor_id}", response_model=AutorRead, responses=NO_EXISTE)
async def obtener_autor(autor_id: int, sesion: SesionDep):
    return await service.obtener(sesion, autor_id)


@router.patch("/{autor_id}", response_model=AutorRead, responses=NO_EXISTE)
async def actualizar_autor(autor_id: int, datos: AutorUpdate, sesion: SesionDep):
    return await service.actualizar(sesion, autor_id, datos)


@router.get("/{autor_id}/libros", response_model=list[LibroDelAutor], responses=NO_EXISTE)
async def libros_del_autor(autor_id: int, pagina: PaginacionDep, sesion: SesionDep):
    return await service.libros_de(sesion, autor_id, pagina)
