from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.paginacion import PaginacionDep
from app.modules.clientes import service
from app.modules.clientes.schemas import (
    ClienteConPerfil,
    ClienteCreate,
    ClienteRead,
    ClienteUpdate,
    PerfilCreate,
    PerfilRead,
    VentaDelCliente,
)

router = APIRouter(prefix="/clientes", tags=["clientes"])

SesionDep = Annotated[AsyncSession, Depends(get_session)]
NO_EXISTE = {404: {"description": "El cliente no existe"}}
EMAIL_REPETIDO = {409: {"description": "Ya existe un cliente con ese email"}}


@router.post("/", response_model=ClienteRead, status_code=status.HTTP_201_CREATED, responses=EMAIL_REPETIDO)
async def crear_cliente(datos: ClienteCreate, sesion: SesionDep):
    return await service.crear(sesion, datos)


@router.get("/{cliente_id}", response_model=ClienteConPerfil, responses=NO_EXISTE)
async def obtener_cliente(cliente_id: int, sesion: SesionDep):
    return await service.obtener(sesion, cliente_id)


@router.patch("/{cliente_id}", response_model=ClienteConPerfil, responses={**NO_EXISTE, **EMAIL_REPETIDO})
async def actualizar_cliente(cliente_id: int, datos: ClienteUpdate, sesion: SesionDep):
    return await service.actualizar(sesion, cliente_id, datos)


@router.post(
    "/{cliente_id}/perfil",
    response_model=PerfilRead,
    status_code=status.HTTP_201_CREATED,
    responses={**NO_EXISTE, 409: {"description": "El cliente ya tiene un perfil"}},
)
async def crear_perfil(cliente_id: int, datos: PerfilCreate, sesion: SesionDep):
    return await service.crear_perfil(sesion, cliente_id, datos)


@router.get("/{cliente_id}/ventas", response_model=list[VentaDelCliente], responses=NO_EXISTE)
async def ventas_del_cliente(cliente_id: int, pagina: PaginacionDep, sesion: SesionDep):
    return await service.ventas_de(sesion, cliente_id, pagina)
