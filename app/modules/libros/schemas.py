"""Contratos de libros.

El alta recibe ids de cosas que ya existen (editorial_id, genero_id y autor_id
de cada autoría) más los datos propios de la relación (rol y orden).
"""

from decimal import Decimal
from typing import Literal

from pydantic import ConfigDict, field_validator, model_validator
from sqlmodel import Field, SQLModel

from app.modules.libros.models import Libro

Rol = Literal["autor", "coautor", "traductor", "ilustrador"]


class AutoriaCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    autor_id: int
    rol: Rol
    orden: int = Field(ge=1)


class LibroCreate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    isbn: str = Field(min_length=1, max_length=20)
    titulo: str = Field(min_length=1, max_length=200)
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    editorial_id: int
    genero_id: int | None = None
    autores: list[AutoriaCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def autores_sin_repetir(self) -> "LibroCreate":
        ids = [autoria.autor_id for autoria in self.autores]
        if len(ids) != len(set(ids)):
            raise ValueError("un mismo autor no puede figurar dos veces en el libro")
        return self


class LibroUpdate(SQLModel):
    """PATCH: se aplican sólo los campos enviados. genero_id admite null (quita el género)."""

    model_config = ConfigDict(extra="forbid")

    isbn: str | None = Field(default=None, min_length=1, max_length=20)
    titulo: str | None = Field(default=None, min_length=1, max_length=200)
    precio: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    editorial_id: int | None = None
    genero_id: int | None = None

    @field_validator("isbn", "titulo", "precio", "stock", "editorial_id")
    @classmethod
    def no_nulo(cls, valor):
        if valor is None:
            raise ValueError("no puede ser nulo")
        return valor


class EditorialResumen(SQLModel):
    id: int
    nombre: str


class GeneroResumen(SQLModel):
    id: int
    nombre: str


class AutoriaRead(SQLModel):
    autor_id: int
    nombre: str
    rol: str
    orden: int


class LibroListado(SQLModel):
    """Libro con su editorial y su género (listado)."""

    id: int
    isbn: str
    titulo: str
    precio: Decimal
    stock: int
    editorial: EditorialResumen
    genero: GeneroResumen | None

    @classmethod
    def desde(cls, libro: Libro) -> "LibroListado":
        return cls(**_campos_de_listado(libro))


class LibroDetalle(LibroListado):
    """Libro con editorial, género y autores (con rol y orden)."""

    autores: list[AutoriaRead]

    @classmethod
    def desde(cls, libro: Libro) -> "LibroDetalle":
        return cls(
            **_campos_de_listado(libro),
            autores=[
                AutoriaRead(
                    autor_id=autoria.autor_id,
                    nombre=autoria.autor.nombre,
                    rol=autoria.rol,
                    orden=autoria.orden,
                )
                for autoria in libro.autorias
            ],
        )


def _campos_de_listado(libro: Libro) -> dict:
    return {
        "id": libro.id,
        "isbn": libro.isbn,
        "titulo": libro.titulo,
        "precio": libro.precio,
        "stock": libro.stock,
        "editorial": EditorialResumen(id=libro.editorial.id, nombre=libro.editorial.nombre),
        "genero": GeneroResumen(id=libro.genero.id, nombre=libro.genero.nombre) if libro.genero else None,
    }
