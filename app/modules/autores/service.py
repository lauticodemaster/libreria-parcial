"""Lógica de autores. Recibe la sesión como parámetro."""

from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import confirmar, no_encontrado
from app.core.paginacion import Paginacion
from app.modules.autores.models import Autor
from app.modules.autores.schemas import AutorCreate, AutorUpdate, LibroDelAutor
from app.modules.libros.models import LibroAutor

MENSAJES: dict[str, str] = {}


async def crear(sesion: AsyncSession, datos: AutorCreate) -> Autor:
    autor = Autor.model_validate(datos)
    sesion.add(autor)
    await confirmar(sesion, MENSAJES)
    return autor


async def listar(sesion: AsyncSession, pagina: Paginacion) -> list[Autor]:
    consulta = select(Autor).order_by(Autor.id).offset(pagina.offset).limit(pagina.limit)
    return list(await sesion.exec(consulta))


async def obtener(sesion: AsyncSession, autor_id: int) -> Autor:
    autor = await sesion.get(Autor, autor_id)
    if autor is None:
        raise no_encontrado("El autor")
    return autor


async def actualizar(sesion: AsyncSession, autor_id: int, datos: AutorUpdate) -> Autor:
    autor = await obtener(sesion, autor_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(autor, campo, valor)
    sesion.add(autor)
    await confirmar(sesion, MENSAJES)
    return autor


async def libros_de(sesion: AsyncSession, autor_id: int, pagina: Paginacion) -> list[LibroDelAutor]:
    """Libros del autor con rol y orden. El libro de cada autoría (relación a
    uno) se precarga con joinedload en la misma consulta: sin N+1."""
    await obtener(sesion, autor_id)
    consulta = (
        select(LibroAutor)
        .where(LibroAutor.autor_id == autor_id)
        .options(joinedload(LibroAutor.libro))
        .order_by(LibroAutor.libro_id)
        .offset(pagina.offset)
        .limit(pagina.limit)
    )
    autorias = await sesion.exec(consulta)
    return [
        LibroDelAutor(
            libro_id=autoria.libro_id,
            isbn=autoria.libro.isbn,
            titulo=autoria.libro.titulo,
            rol=autoria.rol,
            orden=autoria.orden,
        )
        for autoria in autorias
    ]
