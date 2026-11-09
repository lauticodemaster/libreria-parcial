"""Tablas cliente y perfil_cliente.

Cliente ↔ PerfilCliente es UNO A UNO: un cliente tiene como máximo un perfil.
La clave foránea va en perfil_cliente.cliente_id (el perfil depende del
cliente, no al revés) y lleva UNIQUE: es lo que impide un segundo perfil
(RN-09). Ese UNIQUE crea además el índice de la clave foránea.
Cliente.perfil devuelve un objeto (uselist=False), no una lista.
"""

from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.ventas.models import Venta


class Cliente(SQLModel, table=True):
    __tablename__ = "cliente"
    __table_args__ = (UniqueConstraint("email", name="uq_cliente_email"),)

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=120)
    email: str = Field(max_length=200)

    perfil: Optional["PerfilCliente"] = Relationship(
        back_populates="cliente",
        sa_relationship_kwargs={"uselist": False, "lazy": "raise"},
    )
    ventas: list["Venta"] = Relationship(
        back_populates="cliente",
        sa_relationship_kwargs={"lazy": "raise"},
    )


class PerfilCliente(SQLModel, table=True):
    __tablename__ = "perfil_cliente"
    __table_args__ = (UniqueConstraint("cliente_id", name="uq_perfil_cliente_cliente_id"),)

    id: int | None = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="cliente.id")
    telefono: str = Field(max_length=40)
    direccion: str = Field(max_length=200)

    cliente: "Cliente" = Relationship(
        back_populates="perfil",
        sa_relationship_kwargs={"lazy": "raise"},
    )
