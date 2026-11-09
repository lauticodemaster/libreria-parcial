"""Aplicación FastAPI: lifespan y registro de routers."""

import importlib
import logging
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.config import leer_configuracion
from app.core.database import crear_fabrica_de_sesiones, crear_motor, crear_tablas
from app.core.errores import MENSAJE_GENERICO

# Todos los modelos de tabla se importan ANTES de create_all, para que
# SQLModel.metadata los conozca a todos.
from app.modules.autores.models import Autor  # noqa: F401
from app.modules.clientes.models import Cliente, PerfilCliente  # noqa: F401
from app.modules.editoriales.models import Editorial  # noqa: F401
from app.modules.generos.models import Genero  # noqa: F401
from app.modules.libros.models import Libro, LibroAutor  # noqa: F401
from app.modules.ventas.models import RenglonVenta, Venta  # noqa: F401


def configurar_log() -> logging.Logger:
    """Logger propio de la aplicación ("libreria"), con salida a la consola."""
    logger = logging.getLogger("libreria")
    if not logger.handlers:
        manejador = logging.StreamHandler(sys.stdout)
        manejador.setFormatter(logging.Formatter("%(levelname)s:     %(name)s - %(message)s"))
        logger.addHandler(manejador)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


logger = configurar_log()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Si falta DATABASE_URL o la base no responde, la excepción corta el
    # arranque y el proceso termina con error: no queda atendiendo sin base.
    configuracion = leer_configuracion()
    motor = crear_motor(configuracion.database_url, echo=configuracion.sql_echo)
    app.state.motor = motor
    app.state.fabrica_sesiones = crear_fabrica_de_sesiones(motor)
    try:
        await crear_tablas(motor)
        logger.info("Tablas verificadas: create_all creó las que faltaban.")
        yield
    finally:
        await motor.dispose()
        logger.info("Motor de base de datos cerrado.")


app = FastAPI(
    title="Librería",
    description="API del catálogo y las ventas de una librería de barrio (Parcial de Programación III).",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(IntegrityError)
async def integridad_no_traducida(request: Request, exc: IntegrityError) -> JSONResponse:
    """Red de seguridad (RN-12): si algún IntegrityError llegara sin traducir,
    se responde 409 con un mensaje propio y nunca con el texto de la base."""
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": MENSAJE_GENERICO})


# Registro de routers: cada módulo expone `router` en app/modules/<módulo>/router.py.
MODULOS = ("health", "editoriales", "generos", "autores", "libros", "clientes", "ventas")


def registrar_routers(aplicacion: FastAPI) -> None:
    for nombre in MODULOS:
        ruta = f"app.modules.{nombre}.router"
        try:
            modulo = importlib.import_module(ruta)
        except ModuleNotFoundError as error:
            # Permite que el repositorio arranque mientras cada integrante
            # incorpora su módulo; con el proyecto completo no se omite ninguno.
            if error.name != ruta:
                raise
            logger.warning("El módulo %s todavía no tiene router; se omite.", nombre)
            continue
        aplicacion.include_router(modulo.router)


registrar_routers(app)
