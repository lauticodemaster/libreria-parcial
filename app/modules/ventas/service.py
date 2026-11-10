"""Lógica de ventas. Recibe la sesión como parámetro.

- La venta se crea con sus renglones (RN-04): se agregan a venta.renglones y
  se guardan en la misma transacción. No hay alta de renglones por separado.
- El precio de cada renglón se lee del libro en la base y se copia (RN-06).
- El total lo calcula el servidor: suma de cantidad × precio unitario (RN-07).
- Las ventas no se modifican (RN-08): no hay PATCH ni DELETE.
- El detalle precarga cliente (joinedload) y renglones con su libro
  (selectinload + joinedload): siempre 2 consultas, con uno o con muchos renglones.
"""

import asyncio
import logging
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import confirmar, no_encontrado
from app.core.paginacion import Paginacion
from app.modules.libros.models import Libro
from app.modules.ventas.models import RenglonVenta, Venta
from app.modules.ventas.schemas import CENTAVOS, VentaCreate, VentaRead

logger = logging.getLogger("libreria.ventas")

MENSAJES = {
    "venta_cliente_id_fkey": "El cliente indicado no existe.",
    "renglon_venta_libro_id_fkey": "Alguno de los libros indicados no existe.",
    "uq_renglon_venta_venta_libro": "Un mismo libro no puede aparecer en dos renglones.",
    "ck_renglon_venta_cantidad_positiva": "La cantidad de cada renglón tiene que ser mayor que cero.",
    "ck_venta_total_no_negativo": "El total de la venta no puede ser negativo.",
}


def _consulta_de_detalle():
    return select(Venta).options(
        joinedload(Venta.cliente),
        selectinload(Venta.renglones).joinedload(RenglonVenta.libro),
    ).execution_options(populate_existing=True)


async def obtener(sesion: AsyncSession, venta_id: int) -> VentaRead:
    venta = (await sesion.exec(_consulta_de_detalle().where(Venta.id == venta_id))).first()
    if venta is None:
        raise no_encontrado("La venta")
    return VentaRead.desde(venta)


async def listar(sesion: AsyncSession, pagina: Paginacion) -> list[VentaRead]:
    consulta = _consulta_de_detalle().order_by(Venta.id).offset(pagina.offset).limit(pagina.limit)
    return [VentaRead.desde(venta) for venta in await sesion.exec(consulta)]


async def crear(sesion: AsyncSession, datos: VentaCreate) -> VentaRead:
    ids = [renglon.libro_id for renglon in datos.renglones]
    # El precio no viaja en el DTO: el servidor lo lee de la base (una sola consulta, parámetros ligados).
    precios = dict((await sesion.exec(select(Libro.id, Libro.precio).where(Libro.id.in_(ids)))).all())
    faltantes = [libro_id for libro_id in ids if libro_id not in precios]
    if faltantes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No existe el libro con id {faltantes[0]}.",
        )

    renglones = [
        RenglonVenta(libro_id=r.libro_id, cantidad=r.cantidad, precio_unitario=precios[r.libro_id])
        for r in datos.renglones
    ]
    total = sum((r.cantidad * r.precio_unitario for r in renglones), Decimal("0")).quantize(CENTAVOS)
    venta = Venta(cliente_id=datos.cliente_id, total=total, renglones=renglones)
    sesion.add(venta)
    # Si el cliente no existe, la base rechaza la clave foránea → 409 con mensaje propio.
    await confirmar(sesion, MENSAJES)
    return await obtener(sesion, venta.id)


async def avisar_comprobante(venta_id: int, email: str, total: Decimal) -> None:
    """Aviso del comprobante al cliente (simulado). Corre con BackgroundTasks
    DESPUÉS de enviar la respuesta; el await libera el bucle de eventos, así que
    mientras espera el servidor sigue atendiendo otras peticiones."""
    await asyncio.sleep(0.5)
    logger.info("Comprobante de la venta %s enviado a %s (total $%s).", venta_id, email, total)
