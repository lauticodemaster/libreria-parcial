"""Tabla genero.

Libro → Genero es una AGREGACIÓN OPCIONAL: el libro puede incorporar un género
que ya existe, o no tener ninguno. La clave foránea va en libro.genero_id y
admite nulo.
"""

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import Libro


class Genero(SQLModel, table=True):
    __tablename__ = "genero"
    __table_args__ = (UniqueConstraint("nombre", name="uq_genero_nombre"),)

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=80)

    libros: list["Libro"] = Relationship(
        back_populates="genero",
        sa_relationship_kwargs={"lazy": "raise"},
    )
