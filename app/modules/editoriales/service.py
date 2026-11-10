"""Lógica de editoriales. Recibe la sesión como parámetro.

La unicidad del nombre la garantiza la base (uq_editorial_nombre): no se
consulta antes si el nombre existe; se escribe y, si la base lo rechaza, se
responde 409 con un mensaje propio.
"""

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import confirmar, no_encontrado
from app.core.paginacion import Paginacion
from app.modules.editoriales.models import Editorial
from app.modules.editoriales.schemas import EditorialCreate, EditorialUpdate
from app.modules.libros.models import Libro

MENSAJES = {"uq_editorial_nombre": "Ya existe una editorial con ese nombre."}


async def crear(sesion: AsyncSession, datos: EditorialCreate) -> Editorial:
    editorial = Editorial.model_validate(datos)
    sesion.add(editorial)
    await confirmar(sesion, MENSAJES)
    return editorial


async def listar(sesion: AsyncSession, pagina: Paginacion) -> list[Editorial]:
    consulta = select(Editorial).order_by(Editorial.id).offset(pagina.offset).limit(pagina.limit)
    return list(await sesion.exec(consulta))


async def obtener(sesion: AsyncSession, editorial_id: int) -> Editorial:
    editorial = await sesion.get(Editorial, editorial_id)
    if editorial is None:
        raise no_encontrado("La editorial")
    return editorial


async def actualizar(sesion: AsyncSession, editorial_id: int, datos: EditorialUpdate) -> Editorial:
    editorial = await obtener(sesion, editorial_id)
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(editorial, campo, valor)
    sesion.add(editorial)
    await confirmar(sesion, MENSAJES)
    return editorial


async def libros_de(sesion: AsyncSession, editorial_id: int, pagina: Paginacion) -> list[Libro]:
    await obtener(sesion, editorial_id)
    consulta = (
        select(Libro)
        .where(Libro.editorial_id == editorial_id)
        .order_by(Libro.id)
        .offset(pagina.offset)
        .limit(pagina.limit)
    )
    return list(await sesion.exec(consulta))
