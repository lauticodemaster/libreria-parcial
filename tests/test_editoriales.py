from decimal import Decimal

import pytest

from app.modules.editoriales.models import Editorial
from app.modules.libros.models import Libro

pytestmark = pytest.mark.anyio

TEXTOS_INTERNOS = ("uq_", "duplicate", "violates", "constraint", "unique")


def sin_texto_interno(mensaje: str) -> bool:
    return not any(t in mensaje.lower() for t in TEXTOS_INTERNOS)


async def test_crear_editorial_devuelve_201_con_id(cliente):
    respuesta = await cliente.post("/editoriales/", json={"nombre": "Sudamericana", "pais": "Argentina"})

    assert respuesta.status_code == 201
    assert respuesta.json() == {"id": 1, "nombre": "Sudamericana", "pais": "Argentina"}


async def test_el_alta_no_acepta_id_ni_campos_vacios(cliente):
    sin_pais = await cliente.post("/editoriales/", json={"nombre": "Emecé"})
    nombre_vacio = await cliente.post("/editoriales/", json={"nombre": "", "pais": "Argentina"})
    con_id = await cliente.post("/editoriales/", json={"id": 7, "nombre": "Emecé", "pais": "Argentina"})

    assert sin_pais.status_code == 422
    assert nombre_vacio.status_code == 422
    assert con_id.status_code == 422


async def test_nombre_repetido_responde_409_con_mensaje_propio(cliente):
    await cliente.post("/editoriales/", json={"nombre": "Anagrama", "pais": "España"})

    respuesta = await cliente.post("/editoriales/", json={"nombre": "Anagrama", "pais": "Chile"})

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "Ya existe una editorial con ese nombre."
    assert sin_texto_interno(respuesta.json()["detail"])


async def test_listado_paginado(cliente, insertar):
    await insertar(*[Editorial(nombre=f"Editorial {i}", pais="Argentina") for i in range(1, 26)])

    por_defecto = await cliente.get("/editoriales/")
    segunda_pagina = await cliente.get("/editoriales/", params={"limit": 10, "offset": 20})

    assert por_defecto.status_code == 200
    assert len(por_defecto.json()) == 20
    assert [e["nombre"] for e in segunda_pagina.json()] == [f"Editorial {i}" for i in range(21, 26)]


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 101}, {"offset": -1}, {"limit": "diez"}])
async def test_paginacion_fuera_de_rango_responde_422(cliente, params):
    respuesta = await cliente.get("/editoriales/", params=params)

    assert respuesta.status_code == 422


async def test_detalle_404_y_422(cliente):
    inexistente = await cliente.get("/editoriales/99")
    no_entero = await cliente.get("/editoriales/abc")

    assert inexistente.status_code == 404
    assert inexistente.json()["detail"] == "La editorial no existe."
    assert no_entero.status_code == 422


async def test_patch_aplica_solo_los_campos_enviados(cliente):
    await cliente.post("/editoriales/", json={"nombre": "Emece", "pais": "Argentina"})

    respuesta = await cliente.patch("/editoriales/1", json={"nombre": "Emecé"})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": 1, "nombre": "Emecé", "pais": "Argentina"}


async def test_patch_con_nombre_repetido_responde_409(cliente):
    await cliente.post("/editoriales/", json={"nombre": "Anagrama", "pais": "España"})
    await cliente.post("/editoriales/", json={"nombre": "Emecé", "pais": "Argentina"})

    respuesta = await cliente.patch("/editoriales/2", json={"nombre": "Anagrama"})

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "Ya existe una editorial con ese nombre."


async def test_patch_rechaza_nulos_y_responde_404_si_no_existe(cliente):
    await cliente.post("/editoriales/", json={"nombre": "Anagrama", "pais": "España"})

    nulo = await cliente.patch("/editoriales/1", json={"nombre": None})
    inexistente = await cliente.patch("/editoriales/99", json={"pais": "Chile"})

    assert nulo.status_code == 422
    assert inexistente.status_code == 404


async def test_libros_de_la_editorial(cliente, insertar):
    sudamericana = Editorial(nombre="Sudamericana", pais="Argentina")
    otra = Editorial(nombre="Emecé", pais="Argentina")
    await insertar(sudamericana, otra)
    await insertar(
        Libro(isbn="111", titulo="Rayuela", precio=Decimal("25000.00"), stock=3, editorial_id=sudamericana.id),
        Libro(isbn="222", titulo="Ficciones", precio=Decimal("20000.00"), stock=1, editorial_id=otra.id),
    )

    respuesta = await cliente.get(f"/editoriales/{sudamericana.id}/libros")
    inexistente = await cliente.get("/editoriales/99/libros")

    assert respuesta.status_code == 200
    assert respuesta.json() == [
        {"id": 1, "isbn": "111", "titulo": "Rayuela", "precio": "25000.00", "stock": 3}
    ]
    assert inexistente.status_code == 404
