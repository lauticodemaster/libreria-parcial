"""Lógica de clientes y perfiles. Recibe la sesión como parámetro.

- El email único lo garantiza la base (uq_cliente_email) → 409.
- Un cliente tiene como máximo un perfil (RN-09): lo garantiza el UNIQUE de
  perfil_cliente.cliente_id → 409. Si el cliente no existe, la base rechaza la
  clave foránea y se responde 404.
"""

from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import confirmar, no_encontrado
from app.core.paginacion import Paginacion
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.clientes.schemas import ClienteConPerfil, ClienteCreate, ClienteUpdate, PerfilCreate
from app.modules.ventas.models import Venta

MENSAJES_CLIENTE = {"uq_cliente_email": "Ya existe un cliente con ese email."}
MENSAJES_PERFIL = {
    "uq_perfil_cliente_cliente_id": "El cliente ya tiene un perfil cargado.",
    "perfil_cliente_cliente_id_fkey": "El cliente no existe.",
}
CODIGOS_PERFIL = {"perfil_cliente_cliente_id_fkey": 404}


async def crear(sesion: AsyncSession, datos: ClienteCreate) -> Cliente:
    cliente = Cliente.model_validate(datos)
    sesion.add(cliente)
    await confirmar(sesion, MENSAJES_CLIENTE)
    return cliente


async def _con_perfil(sesion: AsyncSession, cliente_id: int) -> Cliente:
    """El perfil (relación a uno) se precarga con joinedload en la misma consulta."""
    consulta = (
        select(Cliente)
        .where(Cliente.id == cliente_id)
        .options(joinedload(Cliente.perfil))
        .execution_options(populate_existing=True)
    )
    cliente = (await sesion.exec(consulta)).first()
    if cliente is None:
        raise no_encontrado("El cliente")
    return cliente


async def obtener(sesion: AsyncSession, cliente_id: int) -> ClienteConPerfil:
    return ClienteConPerfil.desde(await _con_perfil(sesion, cliente_id))


async def actualizar(sesion: AsyncSession, cliente_id: int, datos: ClienteUpdate) -> ClienteConPerfil:
    cliente = await _con_perfil(sesion, cliente_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    sesion.add(cliente)
    await confirmar(sesion, MENSAJES_CLIENTE)
    return ClienteConPerfil.desde(cliente)


async def crear_perfil(sesion: AsyncSession, cliente_id: int, datos: PerfilCreate) -> PerfilCliente:
    perfil = PerfilCliente(cliente_id=cliente_id, **datos.model_dump())
    sesion.add(perfil)
    await confirmar(sesion, MENSAJES_PERFIL, CODIGOS_PERFIL)
    return perfil


async def ventas_de(sesion: AsyncSession, cliente_id: int, pagina: Paginacion) -> list[Venta]:
    if await sesion.get(Cliente, cliente_id) is None:
        raise no_encontrado("El cliente")
    consulta = (
        select(Venta)
        .where(Venta.cliente_id == cliente_id)
        .order_by(Venta.id)
        .offset(pagina.offset)
        .limit(pagina.limit)
    )
    return list(await sesion.exec(consulta))
