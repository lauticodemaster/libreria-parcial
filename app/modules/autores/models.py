"""Tabla autor.

Libro ↔ Autor es MUCHOS A MUCHOS CON DATOS: la relación tiene rol y orden, que
no son ni del libro ni del autor. Por eso se modela con el objeto de asociación
LibroAutor (app/modules/libros/models.py), y el autor llega a sus libros con
autor.autorias[i].libro.
"""

from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.libros.models import LibroAutor


class Autor(SQLModel, table=True):
    __tablename__ = "autor"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=120)
    nacionalidad: str = Field(max_length=80)

    autorias: list["LibroAutor"] = Relationship(
        back_populates="autor",
        sa_relationship_kwargs={"lazy": "raise"},
    )
