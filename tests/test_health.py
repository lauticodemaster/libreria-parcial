import pytest
from sqlalchemy import inspect
from sqlmodel import SQLModel

from app.core import config

pytestmark = pytest.mark.anyio


async def test_live_responde_vivo_sin_tocar_la_base(cliente):
    respuesta = await cliente.get("/health/live")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "vivo"}


async def test_ready_ejecuta_select_1_y_responde_listo(cliente, contador):
    with contador.contar():
        respuesta = await cliente.get("/health/ready")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "listo", "base": "ok"}
    assert contador.consultas == ["SELECT 1"]


async def test_el_lifespan_crea_todas_las_tablas_obligatorias(aplicacion):
    obligatorias = {
        "editorial", "genero", "autor", "libro", "libro_autor",
        "cliente", "perfil_cliente", "venta", "renglon_venta",
    }

    assert obligatorias <= set(SQLModel.metadata.tables)
    async with aplicacion.state.motor.connect() as conexion:
        existentes = await conexion.run_sync(lambda sync: set(inspect(sync).get_table_names()))
    assert obligatorias <= existentes


async def test_la_fabrica_de_sesiones_no_expira_al_hacer_commit(aplicacion):
    assert aplicacion.state.fabrica_sesiones.kw["expire_on_commit"] is False


def test_sin_database_url_la_configuracion_falla(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(config, "load_dotenv", lambda: None)

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        config.leer_configuracion()


@pytest.mark.parametrize(("valor", "esperado"), [("true", True), ("1", True), ("false", False), ("", False)])
def test_sql_echo_se_lee_del_entorno(monkeypatch, valor, esperado):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:c@servidor/base")
    monkeypatch.setenv("SQL_ECHO", valor)
    monkeypatch.setattr(config, "load_dotenv", lambda: None)

    assert config.leer_configuracion().sql_echo is esperado
