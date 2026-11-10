"""Datos iniciales: deja la base en un estado conocido.

    python -m app.seed                      # en la máquina del grupo
    docker exec libreria python -m app.seed # en el contenedor

Crea las tablas que falten, VACÍA todas las tablas del proyecto (reinicia los
ids) y carga un catálogo chico con el que se corren los casos de test/*.http.
Se puede correr las veces que haga falta.
"""

import asyncio
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import leer_configuracion
from app.core.database import crear_fabrica_de_sesiones, crear_motor, crear_tablas
from app.modules.autores.models import Autor
from app.modules.clientes.models import Cliente, PerfilCliente
from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.libros.models import Libro, LibroAutor
from app.modules.ventas.models import RenglonVenta, Venta

TABLAS = "renglon_venta, venta, perfil_cliente, cliente, libro_autor, libro, autor, genero, editorial"


def _grupos() -> list[list]:
    """Grupos en orden de inserción: los ids salen 1, 2, 3... en ese orden."""
    return [
        [
            Editorial(nombre="Sudamericana", pais="Argentina"),     # 1
            Editorial(nombre="Emecé", pais="Argentina"),            # 2
            Editorial(nombre="Anagrama", pais="España"),            # 3
        ],
        [
            Genero(nombre="Novela"),                                # 1
            Genero(nombre="Cuento"),                                # 2
            Genero(nombre="Ensayo"),                                # 3
        ],
        [
            Autor(nombre="Julio Cortázar", nacionalidad="Argentina"),       # 1
            Autor(nombre="Ricardo Piglia", nacionalidad="Argentina"),       # 2
            Autor(nombre="Adolfo Bioy Casares", nacionalidad="Argentina"),  # 3
            Autor(nombre="Silvina Ocampo", nacionalidad="Argentina"),       # 4
            Autor(nombre="Jorge Luis Borges", nacionalidad="Argentina"),    # 5
        ],
        [
            Libro(isbn="978-950-00-0001-1", titulo="Rayuela", precio=Decimal("25000.00"), stock=10,
                  editorial_id=1, genero_id=1),                                                     # 1
            Libro(isbn="978-950-00-0002-2", titulo="Bestiario", precio=Decimal("18000.00"), stock=8,
                  editorial_id=1, genero_id=2),                                                     # 2
            Libro(isbn="978-950-00-0003-3", titulo="La invención de Morel", precio=Decimal("22000.00"),
                  stock=5, editorial_id=2, genero_id=1),                                            # 3
            Libro(isbn="978-950-00-0004-4", titulo="Respiración artificial", precio=Decimal("27000.00"),
                  stock=6, editorial_id=3, genero_id=1),                                            # 4
            Libro(isbn="978-950-00-0005-5", titulo="Ficciones", precio=Decimal("20000.00"), stock=12,
                  editorial_id=2, genero_id=2),                                                     # 5
            # Sin género: la agregación con género es optativa.
            Libro(isbn="978-950-00-0010-0", titulo="Antología de la literatura fantástica",
                  precio=Decimal("30000.00"), stock=3, editorial_id=1, genero_id=None),             # 6
        ],
        [
            LibroAutor(libro_id=1, autor_id=1, rol="autor", orden=1),
            LibroAutor(libro_id=2, autor_id=1, rol="autor", orden=1),
            LibroAutor(libro_id=3, autor_id=3, rol="autor", orden=1),
            LibroAutor(libro_id=4, autor_id=2, rol="autor", orden=1),
            LibroAutor(libro_id=5, autor_id=5, rol="autor", orden=1),
            LibroAutor(libro_id=6, autor_id=5, rol="coautor", orden=1),
            LibroAutor(libro_id=6, autor_id=4, rol="coautor", orden=2),
            LibroAutor(libro_id=6, autor_id=3, rol="coautor", orden=3),
        ],
        [
            Cliente(nombre="Ana Pérez", email="ana@example.com"),       # 1 (con perfil)
            Cliente(nombre="Tomás Ríos", email="tomas@example.com"),    # 2 (sin perfil)
            Cliente(nombre="Lucía Gómez", email="lucia@example.com"),   # 3
        ],
        [
            PerfilCliente(cliente_id=1, telefono="11 4567-8901", direccion="Av. Corrientes 1234, CABA"),
        ],
        [
            # Venta 1 (así la venta del caso C-06 sale con id 2, como en la consigna).
            Venta(
                cliente_id=1,
                total=Decimal("22000.00"),
                renglones=[RenglonVenta(libro_id=3, cantidad=1, precio_unitario=Decimal("22000.00"))],
            ),
        ],
    ]


async def cargar(motor: AsyncEngine) -> None:
    await crear_tablas(motor)
    async with motor.begin() as conexion:
        await conexion.execute(text(f"TRUNCATE {TABLAS} RESTART IDENTITY CASCADE"))
    fabrica = crear_fabrica_de_sesiones(motor)
    async with fabrica() as sesion:
        for grupo in _grupos():
            sesion.add_all(grupo)
            await sesion.flush()
        await sesion.commit()


async def main() -> None:
    configuracion = leer_configuracion()
    motor = crear_motor(configuracion.database_url, echo=False)
    try:
        await cargar(motor)
    finally:
        await motor.dispose()
    print("Datos iniciales cargados: 3 editoriales, 3 géneros, 5 autores, 6 libros, 3 clientes y 1 venta.")


if __name__ == "__main__":
    asyncio.run(main())
