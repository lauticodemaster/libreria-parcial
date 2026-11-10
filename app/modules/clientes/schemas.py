"""Contratos de clientes y de su perfil."""

from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, EmailStr, field_validator
from sqlmodel import Field, SQLModel

from app.modules.clientes.models import Cliente


class ClienteCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120)
    email: EmailStr = Field(max_length=200)


class ClienteUpdate(SQLModel):
    """PATCH: se aplican sólo los campos enviados."""

    model_config = ConfigDict(extra="forbid")

    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = Field(default=None, max_length=200)

    @field_validator("nombre", "email")
    @classmethod
    def no_nulo(cls, valor):
        if valor is None:
            raise ValueError("no puede ser nulo")
        return valor


class ClienteRead(SQLModel):
    id: int
    nombre: str
    email: str


class PerfilCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    telefono: str = Field(min_length=6, max_length=40)
    direccion: str = Field(min_length=3, max_length=200)


class PerfilRead(SQLModel):
    id: int
    cliente_id: int
    telefono: str
    direccion: str


class ClienteConPerfil(ClienteRead):
    """Cliente con su perfil: un objeto (o null), nunca una lista."""

    perfil: PerfilRead | None

    @classmethod
    def desde(cls, cliente: Cliente) -> "ClienteConPerfil":
        perfil = cliente.perfil
        return cls(
            id=cliente.id,
            nombre=cliente.nombre,
            email=cliente.email,
            perfil=PerfilRead.model_validate(perfil) if perfil is not None else None,
        )


class VentaDelCliente(SQLModel):
    id: int
    fecha: datetime
    total: Decimal
