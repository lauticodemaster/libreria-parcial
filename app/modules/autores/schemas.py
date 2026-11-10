"""Contratos de autores. Los DTO de alta no llevan id."""

from pydantic import ConfigDict, field_validator
from sqlmodel import Field, SQLModel


class AutorCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=120)
    nacionalidad: str = Field(min_length=1, max_length=80)


class AutorUpdate(SQLModel):
    """PATCH: se aplican sólo los campos enviados."""

    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    nacionalidad: str | None = Field(default=None, min_length=1, max_length=80)

    @field_validator("nombre", "nacionalidad")
    @classmethod
    def no_nulo(cls, valor: str | None) -> str:
        if valor is None:
            raise ValueError("no puede ser nulo")
        return valor


class AutorRead(SQLModel):
    id: int
    nombre: str
    nacionalidad: str


class LibroDelAutor(SQLModel):
    """Un libro del autor con los datos de la relación: rol y orden."""

    libro_id: int
    isbn: str
    titulo: str
    rol: str
    orden: int
