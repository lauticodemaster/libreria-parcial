from decimal import Decimal

import pytest

from app.modules.autores.models import Autor
from app.modules.editoriales.models import Editorial
from app.modules.libros.models import Libro, LibroAutor

pytestmark = pytest.mark.anyio


async def test_crear_y_leer_autor(cliente):
    alta = await cliente.post("/autores/", json={"nombre": "Julio Cortázar", "nacionalidad": "Argentina"})
    detalle = await cliente.get("/autores/1")

    assert alta.status_code == 201
    assert alta.json() == {"id": 1, "nombre": "Julio Cortázar", "nacionalidad": "Argentina"}
    assert detalle.status_code == 200
    assert detalle.json() == alta.json()


async def test_alta_de_autor_invalida_responde_422(cliente):
    respuesta = await cliente.post("/autores/", json={"nombre": ""})

    assert respuesta.status_code == 422


async def test_autor_inexistente_404_y_no_entero_422(cliente):
    assert (await cliente.get("/autores/7")).status_code == 404
    assert (await cliente.get("/autores/siete")).status_code == 422
    assert (await cliente.patch("/autores/7", json={"nombre": "X"})).status_code == 404


async def test_patch_de_autor_es_parcial(cliente):
    await cliente.post("/autores/", json={"nombre": "Silvina Ocampo", "nacionalidad": "Arg."})

    respuesta = await cliente.patch("/autores/1", json={"nacionalidad": "Argentina"})

    assert respuesta.status_code == 200
    assert respuesta.json() == {"id": 1, "nombre": "Silvina Ocampo", "nacionalidad": "Argentina"}


async def test_libros_del_autor_con_rol_y_orden(cliente, insertar):
    editorial = Editorial(nombre="Sudamericana", pais="Argentina")
    bioy = Autor(nombre="Adolfo Bioy Casares", nacionalidad="Argentina")
    ocampo = Autor(nombre="Silvina Ocampo", nacionalidad="Argentina")
    await insertar(editorial, bioy, ocampo)
    morel = Libro(isbn="1", titulo="La invención de Morel", precio=Decimal("22000"), stock=1,
                  editorial_id=editorial.id)
    aman = Libro(isbn="2", titulo="Los que aman, odian", precio=Decimal("21000"), stock=1,
                 editorial_id=editorial.id)
    await insertar(morel, aman)
    await insertar(
        LibroAutor(libro_id=morel.id, autor_id=bioy.id, rol="autor", orden=1),
        LibroAutor(libro_id=aman.id, autor_id=ocampo.id, rol="coautor", orden=1),
        LibroAutor(libro_id=aman.id, autor_id=bioy.id, rol="coautor", orden=2),
    )

    respuesta = await cliente.get(f"/autores/{bioy.id}/libros")
    inexistente = await cliente.get("/autores/99/libros")

    assert respuesta.status_code == 200
    assert respuesta.json() == [
        {"libro_id": 1, "isbn": "1", "titulo": "La invención de Morel", "rol": "autor", "orden": 1},
        {"libro_id": 2, "isbn": "2", "titulo": "Los que aman, odian", "rol": "coautor", "orden": 2},
    ]
    assert inexistente.status_code == 404
