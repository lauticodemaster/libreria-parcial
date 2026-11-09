"""Tabla editorial.

Libro → Editorial es una AGREGACIÓN: el libro incorpora una editorial que ya
existe (viaja su id) y la misma editorial la comparten muchos libros. Por eso la
clave foránea va del lado del libro (libro.editorial_id), el lado "muchos".
"""

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import Libro


class Editorial(SQLModel, table=True):
    __tablename__ = "editorial"
    __table_args__ = (UniqueConstraint("nombre", name="uq_editorial_nombre"),)

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=120)
    pais: str = Field(max_length=80)

    # lazy="raise": ninguna lectura puede depender de la carga perezosa.
    libros: list["Libro"] = Relationship(
        back_populates="editorial",
        sa_relationship_kwargs={"lazy": "raise"},
    )
