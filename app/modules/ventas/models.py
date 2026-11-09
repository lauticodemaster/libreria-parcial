"""Tablas venta y renglon_venta.

- Venta → Cliente es una ASOCIACIÓN: la venta conoce al cliente que compró
  (venta.cliente_id), pero ninguno es parte del otro.
- Venta ◆ RenglonVenta es una COMPOSICIÓN: un renglón no tiene sentido sin su
  venta y nace con ella. La clave foránea va en renglon_venta.venta_id, con
  ON DELETE CASCADE y cascade="all, delete-orphan" en el ORM.
- RenglonVenta → Libro es una ASOCIACIÓN: el renglón nombra un libro que ya
  existe. El precio_unitario se copia del libro al registrar la venta (RN-06).
"""

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Column, DateTime, UniqueConstraint, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.clientes.models import Cliente
    from app.modules.libros.models import Libro


def ahora_utc() -> datetime:
    return datetime.now(UTC)


class Venta(SQLModel, table=True):
    __tablename__ = "venta"
    __table_args__ = (CheckConstraint("total >= 0", name="ck_venta_total_no_negativo"),)

    id: int | None = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id", index=True)
    # Fecha con zona horaria (timestamptz).
    fecha: datetime = Field(
        default_factory=ahora_utc,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )
    total: Decimal = Field(default=Decimal("0.00"), max_digits=12, decimal_places=2)

    cliente: "Cliente" = Relationship(
        back_populates="ventas",
        sa_relationship_kwargs={"lazy": "raise"},
    )
    renglones: list["RenglonVenta"] = Relationship(
        back_populates="venta",
        sa_relationship_kwargs={
            "lazy": "raise",
            "cascade": "all, delete-orphan",
            "order_by": "RenglonVenta.id",
        },
    )


class RenglonVenta(SQLModel, table=True):
    __tablename__ = "renglon_venta"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_renglon_venta_cantidad_positiva"),
        CheckConstraint("precio_unitario > 0", name="ck_renglon_venta_precio_positivo"),
        # Un mismo libro no aparece en dos renglones de la misma venta (RN-05).
        # El índice de este UNIQUE empieza por venta_id: indexa esa clave foránea.
        UniqueConstraint("venta_id", "libro_id", name="uq_renglon_venta_venta_libro"),
    )

    id: int | None = Field(default=None, primary_key=True)
    venta_id: int = Field(foreign_key="venta.id", ondelete="CASCADE")
    libro_id: int = Field(foreign_key="libro.id", index=True)
    cantidad: int
    precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)

    venta: "Venta" = Relationship(
        back_populates="renglones",
        sa_relationship_kwargs={"lazy": "raise"},
    )
    libro: "Libro" = Relationship(
        back_populates="renglones",
        sa_relationship_kwargs={"lazy": "raise"},
    )
