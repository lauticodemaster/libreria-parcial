from decimal import Decimal

import pytest

from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.libros.models import Libro

pytestmark = pytest.mark.anyio


async def test_crear_genero_devuelve_201(cliente):
    respuesta = await cliente.post("/generos/", json={"nombre": "Novela"})

    assert respuesta.status_code == 201
    assert respuesta.json() == {"id": 1, "nombre": "Novela"}


async def test_genero_repetido_responde_409_con_mensaje_propio(cliente):
    await cliente.post("/generos/", json={"nombre": "Cuento"})

    respuesta = await cliente.post("/generos/", json={"nombre": "Cuento"})

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "Ya existe un género con ese nombre."


async def test_listado_de_generos_paginado(cliente, insertar):
    await insertar(Genero(nombre="Novela"), Genero(nombre="Cuento"), Genero(nombre="Ensayo"))

    respuesta = await cliente.get("/generos/", params={"limit": 2, "offset": 1})

    assert respuesta.status_code == 200
    assert respuesta.json() == [{"id": 2, "nombre": "Cuento"}, {"id": 3, "nombre": "Ensayo"}]


async def test_libros_del_genero(cliente, insertar):
    editorial = Editorial(nombre="Emecé", pais="Argentina")
    novela, cuento = Genero(nombre="Novela"), Genero(nombre="Cuento")
    await insertar(editorial, novela, cuento)
    await insertar(
        Libro(isbn="1", titulo="La invención de Morel", precio=Decimal("22000"), stock=2,
              editorial_id=editorial.id, genero_id=novela.id),
        Libro(isbn="2", titulo="Ficciones", precio=Decimal("20000"), stock=5,
              editorial_id=editorial.id, genero_id=cuento.id),
    )

    respuesta = await cliente.get(f"/generos/{cuento.id}/libros")
    inexistente = await cliente.get("/generos/99/libros")

    assert respuesta.status_code == 200
    assert [libro["titulo"] for libro in respuesta.json()] == ["Ficciones"]
    assert inexistente.status_code == 404
    assert inexistente.json()["detail"] == "El género no existe."
