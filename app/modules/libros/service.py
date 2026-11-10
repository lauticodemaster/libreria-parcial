"""Lógica de libros. Recibe la sesión como parámetro.

- En el alta ningún if consulta antes si la editorial, el género o los autores
  existen: se escribe, y si la base rechaza una clave foránea se responde 409.
- Las lecturas precargan todo en la misma consulta: joinedload para las
  relaciones a uno (editorial, género, autor de cada autoría) y selectinload
  para la colección (autorias). El detalle hace siempre 2 consultas, tenga el
  libro uno o muchos autores.
- La búsqueda por título usa un parámetro ligado (RN-11).
"""

from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errores import confirmar, no_encontrado
from app.core.paginacion import Paginacion
from app.modules.libros.models import Libro, LibroAutor
from app.modules.libros.schemas import LibroCreate, LibroDetalle, LibroListado, LibroUpdate

MENSAJES = {
    "uq_libro_isbn": "Ya existe un libro con ese ISBN.",
    "libro_editorial_id_fkey": "La editorial indicada no existe.",
    "libro_genero_id_fkey": "El género indicado no existe.",
    "libro_autor_autor_id_fkey": "Alguno de los autores indicados no existe.",
    "libro_autor_pkey": "Un mismo autor no puede figurar dos veces en el libro.",
    "ck_libro_precio_positivo": "El precio del libro tiene que ser mayor que cero.",
    "ck_libro_stock_no_negativo": "El stock del libro no puede ser negativo.",
    "ck_libro_autor_orden": "El orden de cada autor empieza en 1.",
    "ck_libro_autor_rol": "El rol tiene que ser autor, coautor, traductor o ilustrador.",
}


def _patron_que_contiene(texto: str) -> str:
    """Patrón para ILIKE que busca el texto literal: escapa los comodines % y _.
    El resultado viaja como VALOR de un parámetro ligado, nunca como SQL."""
    escapado = texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escapado}%"


def _consulta_de_detalle():
    return select(Libro).options(
        joinedload(Libro.editorial),
        joinedload(Libro.genero),
        selectinload(Libro.autorias).joinedload(LibroAutor.autor),
    ).execution_options(populate_existing=True)


async def obtener_detalle(sesion: AsyncSession, libro_id: int) -> LibroDetalle:
    libro = (await sesion.exec(_consulta_de_detalle().where(Libro.id == libro_id))).first()
    if libro is None:
        raise no_encontrado("El libro")
    return LibroDetalle.desde(libro)


async def crear(sesion: AsyncSession, datos: LibroCreate) -> LibroDetalle:
    libro = Libro(
        **datos.model_dump(exclude={"autores"}),
        autorias=[
            LibroAutor(autor_id=autoria.autor_id, rol=autoria.rol, orden=autoria.orden)
            for autoria in datos.autores
        ],
    )
    sesion.add(libro)
    await confirmar(sesion, MENSAJES)
    return await obtener_detalle(sesion, libro.id)


async def listar(
    sesion: AsyncSession,
    pagina: Paginacion,
    titulo: str | None = None,
    genero_id: int | None = None,
) -> list[LibroListado]:
    consulta = select(Libro).options(joinedload(Libro.editorial), joinedload(Libro.genero))
    if titulo:
        consulta = consulta.where(Libro.titulo.ilike(_patron_que_contiene(titulo), escape="\\"))
    if genero_id is not None:
        consulta = consulta.where(Libro.genero_id == genero_id)
    consulta = consulta.order_by(Libro.id).offset(pagina.offset).limit(pagina.limit)
    return [LibroListado.desde(libro) for libro in await sesion.exec(consulta)]


async def actualizar(sesion: AsyncSession, libro_id: int, datos: LibroUpdate) -> LibroDetalle:
    libro = await sesion.get(Libro, libro_id)
    if libro is None:
        raise no_encontrado("El libro")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(libro, campo, valor)
    sesion.add(libro)
    await confirmar(sesion, MENSAJES)
    return await obtener_detalle(sesion, libro_id)
