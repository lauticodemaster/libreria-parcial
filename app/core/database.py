"""Motor asincrónico, fábrica de sesiones y dependencia get_session.

El motor y la fábrica se crean en el lifespan (app/main.py) y se guardan en
app.state; acá están las funciones que los construyen y la dependencia que
entrega una sesión por petición.
"""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


def crear_motor(database_url: str, echo: bool = False) -> AsyncEngine:
    """Crea el motor asincrónico. echo=True escribe cada consulta en la consola."""
    return create_async_engine(database_url, echo=echo, pool_pre_ping=True)


def crear_fabrica_de_sesiones(motor: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """expire_on_commit=False: después del commit los objetos siguen legibles
    sin volver a la base (en async, una recarga implícita fallaría)."""
    return async_sessionmaker(motor, class_=AsyncSession, expire_on_commit=False)


async def crear_tablas(motor: AsyncEngine) -> None:
    """Crea las tablas que falten. No altera las que ya existen."""
    async with motor.begin() as conexion:
        await conexion.run_sync(SQLModel.metadata.create_all)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Una sesión por petición, tomada de la fábrica guardada en app.state."""
    fabrica: async_sessionmaker[AsyncSession] = request.app.state.fabrica_sesiones
    async with fabrica() as sesion:
        yield sesion
