"""Configuración de la aplicación.

La dirección de la base se lee de la variable de entorno DATABASE_URL. En la
máquina del grupo se define en un archivo .env (que no se versiona); en el
contenedor llega con --env-file. El proyecto NO trae una dirección por defecto:
si falta, el arranque falla con un error claro.
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

VALORES_VERDADEROS = {"1", "true", "t", "yes", "y", "si", "sí", "on"}


@dataclass(frozen=True)
class Configuracion:
    database_url: str
    sql_echo: bool = False


def leer_configuracion() -> Configuracion:
    """Lee la configuración del entorno (cargando .env si existe)."""
    # load_dotenv no pisa las variables que ya están definidas en el entorno.
    load_dotenv()
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError(
            "Falta la variable de entorno DATABASE_URL. El proyecto no trae una "
            "dirección de base por defecto: definila en .env o pasala con --env-file."
        )
    sql_echo = os.getenv("SQL_ECHO", "false").strip().lower() in VALORES_VERDADEROS
    return Configuracion(database_url=url, sql_echo=sql_echo)
