"""Contratos de géneros. Los DTO de alta no llevan id."""

from decimal import Decimal

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class GeneroCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, max_length=80)


class GeneroRead(SQLModel):
    id: int
    nombre: str


class LibroDelGenero(SQLModel):
    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
