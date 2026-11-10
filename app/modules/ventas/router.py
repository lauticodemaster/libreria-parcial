from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.paginacion import PaginacionDep
from app.modules.ventas import service
from app.modules.ventas.schemas import VentaCreate, VentaRead

# Las ventas registran un hecho: no hay PATCH ni DELETE (RN-08).
router = APIRouter(prefix="/ventas", tags=["ventas"])

# scope="function": la sesión se cierra al terminar el handler, antes de enviar
# la respuesta. Así la conexión vuelve al pool y no queda tomada mientras corre
# el aviso del comprobante en segundo plano.
SesionDep = Annotated[AsyncSession, Depends(get_session, scope="function")]


@router.post(
    "/",
    response_model=VentaRead,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "El cliente o alguno de los libros no existe"}},
)
async def registrar_venta(datos: VentaCreate, sesion: SesionDep, tareas: BackgroundTasks):
    venta = await service.crear(sesion, datos)
    # Se agenda el aviso: corre después de enviar la respuesta.
    tareas.add_task(service.avisar_comprobante, venta.id, venta.cliente.email, venta.total)
    return venta


@router.get("/", response_model=list[VentaRead])
async def listar_ventas(pagina: PaginacionDep, sesion: SesionDep):
    return await service.listar(sesion, pagina)


@router.get("/{venta_id}", response_model=VentaRead, responses={404: {"description": "La venta no existe"}})
async def obtener_venta(venta_id: int, sesion: SesionDep):
    return await service.obtener(sesion, venta_id)
