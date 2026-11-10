"""Contratos de ventas.

El alta recibe el id del cliente (asociación) y los datos de cada renglón
(composición: el renglón nace con la venta). NO viajan el precio, el total ni
la fecha: los pone el servidor (RN-06, RN-07). Si alguien los manda, 422.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, model_validator
from sqlmodel import Field, SQLModel

from app.modules.ventas.models import RenglonVenta, Venta

CENTAVOS = Decimal("0.01")


class RenglonCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    libro_id: int
    cantidad: int = Field(gt=0)


class VentaCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    cliente_id: int
    renglones: list[RenglonCreate] = Field(min_length=1)

    @model_validator(mode="after")
    def libros_sin_repetir(self) -> "VentaCreate":
        """RN-05: un mismo libro no aparece en dos renglones."""
        ids = [renglon.libro_id for renglon in self.renglones]
        if len(ids) != len(set(ids)):
            raise ValueError("un mismo libro no puede aparecer en dos renglones")
        return self


class ClienteDeVenta(SQLModel):
    id: int
    nombre: str
    email: str


class RenglonRead(SQLModel):
    libro_id: int
    titulo: str
    cantidad: int
    precio_unitario: Decimal
    subtotal: Decimal

    @classmethod
    def desde(cls, renglon: RenglonVenta) -> "RenglonRead":
        return cls(
            libro_id=renglon.libro_id,
            titulo=renglon.libro.titulo,
            cantidad=renglon.cantidad,
            precio_unitario=renglon.precio_unitario,
            subtotal=(renglon.cantidad * renglon.precio_unitario).quantize(CENTAVOS),
        )


class VentaRead(SQLModel):
    """Venta con su cliente y sus renglones."""

    id: int
    fecha: datetime
    total: Decimal
    cliente: ClienteDeVenta
    renglones: list[RenglonRead]

    @classmethod
    def desde(cls, venta: Venta) -> "VentaRead":
        return cls(
            id=venta.id,
            fecha=venta.fecha,
            total=venta.total,
            cliente=ClienteDeVenta(id=venta.cliente.id, nombre=venta.cliente.nombre, email=venta.cliente.email),
            renglones=[RenglonRead.desde(renglon) for renglon in venta.renglones],
        )
