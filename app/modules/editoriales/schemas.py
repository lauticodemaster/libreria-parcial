"""Contratos de editoriales. Los DTO de alta no llevan id."""

from decimal import Decimal

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel


class EditorialCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120)
    pais: str = Field(min_length=1, max_length=80)


class EditorialUpdate(SQLModel):
    """PATCH: todos los campos son opcionales; se aplican sólo los enviados."""

    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    pais: str | None = Field(default=None, min_length=1, max_length=80)

    @field_validator("nombre", "pais")
    @classmethod
    def no_nulo(cls, valor: str | None) -> str:
        if valor is None:
            raise ValueError("no puede ser nulo")
        return valor


class EditorialRead(SQLModel):
    id: int
    nombre: str
    pais: str


class LibroDeEditorial(SQLModel):
    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
