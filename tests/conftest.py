"""Infraestructura común de las pruebas automáticas.

Las pruebas corren contra un PostgreSQL real, en la base indicada por
TEST_DATABASE_URL (NUNCA la de trabajo: antes de cada prueba se vacían las
tablas). Si TEST_DATABASE_URL no está definida, las pruebas se saltean.

    TEST_DATABASE_URL=postgresql+asyncpg://usuario:clave@localhost:5432/libreria_test pytest
"""

import os
from collections.abc import AsyncIterator
from contextlib import contextmanager

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event, text

URL_DE_PRUEBA = os.getenv("TEST_DATABASE_URL", "").strip()
if URL_DE_PRUEBA:
    # La aplicación lee DATABASE_URL: en las pruebas apunta a la base de prueba.
    os.environ["DATABASE_URL"] = URL_DE_PRUEBA
    os.environ.setdefault("SQL_ECHO", "false")

TABLAS = "renglon_venta, venta, perfil_cliente, cliente, libro_autor, libro, autor, genero, editorial"


def pytest_collection_modifyitems(config, items):
    if URL_DE_PRUEBA:
        return
    saltear = pytest.mark.skip(reason="Definí TEST_DATABASE_URL para correr las pruebas.")
    for item in items:
        item.add_marker(saltear)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def aplicacion():
    """La aplicación con su lifespan corriendo y las tablas vacías."""
    from app.main import app

    async with app.router.lifespan_context(app):
        async with app.state.motor.begin() as conexion:
            await conexion.execute(text(f"TRUNCATE {TABLAS} RESTART IDENTITY CASCADE"))
        yield app


@pytest.fixture
async def cliente(aplicacion) -> AsyncIterator[AsyncClient]:
    """Cliente HTTP que habla con la aplicación en memoria (sin abrir un puerto)."""
    transporte = ASGITransport(app=aplicacion)
    async with AsyncClient(transport=transporte, base_url="http://prueba") as http:
        yield http


@pytest.fixture
def insertar(aplicacion):
    """Inserta objetos directamente con el ORM, para preparar datos sin pasar por la API."""

    async def _insertar(*objetos):
        async with aplicacion.state.fabrica_sesiones() as sesion:
            for objeto in objetos:
                sesion.add(objeto)
                await sesion.flush()
            await sesion.commit()
        return objetos

    return _insertar


class ContadorDeConsultas:
    def __init__(self, motor):
        self._motor = motor.sync_engine
        self.consultas: list[str] = []

    def _anotar(self, conn, cursor, statement, parameters, context, executemany):
        self.consultas.append(statement)

    @contextmanager
    def contar(self):
        self.consultas = []
        event.listen(self._motor, "before_cursor_execute", self._anotar)
        try:
            yield self
        finally:
            event.remove(self._motor, "before_cursor_execute", self._anotar)

    @property
    def cantidad(self) -> int:
        return len(self.consultas)


@pytest.fixture
def contador(aplicacion) -> ContadorDeConsultas:
    """Cuenta las consultas SQL que llegan a la base (para probar que no hay N+1)."""
    return ContadorDeConsultas(aplicacion.state.motor)
