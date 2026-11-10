"""Lógica de géneros. Recibe la sesión como parámetro."""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import confirmar, no_encontrado
from app.core.paginacion import Paginacion
from app.modules.generos.models import Genero
from app.modules.generos.schemas import GeneroCreate
from app.modules.libros.models import Libro

MENSAJES = {"uq_genero_nombre": "Ya existe un género con ese nombre."}


async def crear(sesion: AsyncSession, datos: GeneroCreate) -> Genero:
    genero = Genero.model_validate(datos)
    sesion.add(genero)
    await confirmar(sesion, MENSAJES)
    return genero


async def listar(sesion: AsyncSession, pagina: Paginacion) -> list[Genero]:
    consulta = select(Genero).order_by(Genero.id).offset(pagina.offset).limit(pagina.limit)
    return list(await sesion.exec(consulta))


async def libros_de(sesion: AsyncSession, genero_id: int, pagina: Paginacion) -> list[Libro]:
    if await sesion.get(Genero, genero_id) is None:
        raise no_encontrado("El género")
    consulta = (
        select(Libro)
        .where(Libro.genero_id == genero_id)
        .order_by(Libro.id)
        .offset(pagina.offset)
        .limit(pagina.limit)
    )
    return list(await sesion.exec(consulta))
