"""Tablas libro y libro_autor.

- libro.editorial_id → editorial.id (agregación, obligatoria).
- libro.genero_id → genero.id (agregación opcional: admite nulo).
- libro_autor es el OBJETO DE ASOCIACIÓN del muchos a muchos entre libro y
  autor: tiene su propia clase porque guarda datos de la relación (rol y orden
  en la tapa). Un link_model escondería esos datos. Para ir de un libro a sus
  autores se navega libro.autorias[i].autor.
"""

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.autores.models import Autor
    from app.modules.editoriales.models import Editorial
    from app.modules.generos.models import Genero
    from app.modules.ventas.models import RenglonVenta

ROLES = ("autor", "coautor", "traductor", "ilustrador")


class LibroAutor(SQLModel, table=True):
    __tablename__ = "libro_autor"
    __table_args__ = (
        CheckConstraint("orden >= 1", name="ck_libro_autor_orden"),
        CheckConstraint(
            "rol IN ('autor', 'coautor', 'traductor', 'ilustrador')",
            name="ck_libro_autor_rol",
        ),
    )

    # Clave primaria compuesta (libro_id, autor_id). Su índice empieza por
    # libro_id, así que esa clave foránea ya queda indexada; autor_id, que es la
    # segunda columna, lleva su propio índice.
    libro_id: int = Field(foreign_key="libro.id", primary_key=True)
    autor_id: int = Field(foreign_key="autor.id", primary_key=True, index=True)
    rol: str = Field(max_length=20)
    orden: int

    libro: "Libro" = Relationship(
        back_populates="autorias",
        sa_relationship_kwargs={"lazy": "raise"},
    )
    autor: "Autor" = Relationship(
        back_populates="autorias",
        sa_relationship_kwargs={"lazy": "raise"},
    )


class Libro(SQLModel, table=True):
    __tablename__ = "libro"
    __table_args__ = (
        UniqueConstraint("isbn", name="uq_libro_isbn"),
        CheckConstraint("precio > 0", name="ck_libro_precio_positivo"),
        CheckConstraint("stock >= 0", name="ck_libro_stock_no_negativo"),
    )

    id: int | None = Field(default=None, primary_key=True)
    isbn: str = Field(max_length=20)
    titulo: str = Field(max_length=200)
    # Dinero con Decimal y NUMERIC(10,2), nunca float.
    precio: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int = Field(default=0)
    editorial_id: int = Field(foreign_key="editorial.id", index=True)
    genero_id: int | None = Field(default=None, foreign_key="genero.id", index=True)

    editorial: "Editorial" = Relationship(
        back_populates="libros",
        sa_relationship_kwargs={"lazy": "raise"},
    )
    genero: Optional["Genero"] = Relationship(
        back_populates="libros",
        sa_relationship_kwargs={"lazy": "raise"},
    )
    autorias: list["LibroAutor"] = Relationship(
        back_populates="libro",
        sa_relationship_kwargs={
            "lazy": "raise",
            "cascade": "all, delete-orphan",
            "order_by": "LibroAutor.orden",
        },
    )
    renglones: list["RenglonVenta"] = Relationship(
        back_populates="libro",
        sa_relationship_kwargs={"lazy": "raise"},
    )
