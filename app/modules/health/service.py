import logging

from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

logger = logging.getLogger("libreria.health")


async def base_responde(sesion: AsyncSession) -> bool:
    """Ejecuta SELECT 1. Devuelve False si la base no responde."""
    try:
        conexion = await sesion.connection()
        await conexion.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 - cualquier falla de conexión significa "no lista"
        logger.warning("La base de datos no respondió al SELECT 1.")
        return False
    return True
