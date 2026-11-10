from decimal import Decimal

import pytest

from app.modules.autores.models import Autor
from app.modules.editoriales.models import Editorial
from app.modules.generos.models import Genero
from app.modules.libros.models import Libro

pytestmark = pytest.mark.anyio


@pytest.fixture
async def catalogo(insertar):
    """Editorial 1, género 1 y autores 1 a 4."""
    await insertar(
        Editorial(nombre="Sudamericana", pais="Argentina"),
        Genero(nombre="Novela"),
        Autor(nombre="Julio Cortázar", nacionalidad="Argentina"),
        Autor(nombre="Ricardo Piglia", nacionalidad="Argentina"),
        Autor(nombre="Adolfo Bioy Casares", nacionalidad="Argentina"),
        Autor(nombre="Silvina Ocampo", nacionalidad="Argentina"),
    )


def alta(**cambios):
    cuerpo = {
        "isbn": "978-950-00-0006-6",
        "titulo": "Los que aman, odian",
        "precio": "21000.00",
        "stock": 4,
        "editorial_id": 1,
        "genero_id": 1,
        "autores": [
            {"autor_id": 4, "rol": "coautor", "orden": 2},
            {"autor_id": 3, "rol": "coautor", "orden": 1},
        ],
    }
    cuerpo.update(cambios)
    return cuerpo


async def test_alta_de_libro_con_ids_y_autorias_devuelve_el_detalle(cliente, catalogo):
    respuesta = await cliente.post("/libros/", json=alta())

    assert respuesta.status_code == 201
    assert respuesta.json() == {
        "id": 1,
        "isbn": "978-950-00-0006-6",
        "titulo": "Los que aman, odian",
        "precio": "21000.00",
        "stock": 4,
        "editorial": {"id": 1, "nombre": "Sudamericana"},
        "genero": {"id": 1, "nombre": "Novela"},
        "autores": [
            {"autor_id": 3, "nombre": "Adolfo Bioy Casares", "rol": "coautor", "orden": 1},
            {"autor_id": 4, "nombre": "Silvina Ocampo", "rol": "coautor", "orden": 2},
        ],
    }


async def test_el_genero_es_optativo(cliente, catalogo):
    respuesta = await cliente.post("/libros/", json=alta(genero_id=None, autores=[]))

    assert respuesta.status_code == 201
    assert respuesta.json()["genero"] is None
    assert respuesta.json()["autores"] == []


async def test_c02_isbn_repetido_responde_409_con_mensaje_propio(cliente, catalogo):
    await cliente.post("/libros/", json=alta())

    respuesta = await cliente.post("/libros/", json=alta(titulo="Otro"))

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "Ya existe un libro con ese ISBN."


async def test_c04_editorial_inexistente_responde_409(cliente, catalogo):
    respuesta = await cliente.post("/libros/", json=alta(editorial_id=999))

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "La editorial indicada no existe."


async def test_c04_autor_inexistente_responde_409_y_no_queda_el_libro(cliente, catalogo):
    respuesta = await cliente.post(
        "/libros/", json=alta(autores=[{"autor_id": 999, "rol": "autor", "orden": 1}])
    )
    listado = await cliente.get("/libros/")

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "Alguno de los autores indicados no existe."
    assert listado.json() == []


async def test_genero_inexistente_responde_409(cliente, catalogo):
    respuesta = await cliente.post("/libros/", json=alta(genero_id=999))

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "El género indicado no existe."


@pytest.mark.parametrize(
    "cambios",
    [
        {"precio": "0"},
        {"precio": "-5"},
        {"stock": -1},
        {"autores": [{"autor_id": 1, "rol": "editor", "orden": 1}]},
        {"autores": [{"autor_id": 1, "rol": "autor", "orden": 0}]},
        {"autores": [{"autor_id": 1, "rol": "autor", "orden": 1}, {"autor_id": 1, "rol": "coautor", "orden": 2}]},
        {"id": 5},
    ],
)
async def test_alta_que_no_cumple_el_contrato_responde_422(cliente, catalogo, cambios):
    respuesta = await cliente.post("/libros/", json=alta(**cambios))

    assert respuesta.status_code == 422


async def test_c01_id_no_entero_responde_422_y_inexistente_404(cliente):
    assert (await cliente.get("/libros/abc")).status_code == 422
    inexistente = await cliente.get("/libros/99")
    assert inexistente.status_code == 404
    assert inexistente.json()["detail"] == "El libro no existe."


async def test_listado_con_editorial_y_genero_filtrado_por_titulo(cliente, catalogo, insertar):
    await insertar(
        Libro(isbn="1", titulo="Rayuela", precio=Decimal("25000"), stock=1, editorial_id=1, genero_id=1),
        Libro(isbn="2", titulo="Bestiario", precio=Decimal("18000"), stock=1, editorial_id=1),
        Libro(isbn="3", titulo="El perseguidor y Rayuela", precio=Decimal("9000"), stock=1, editorial_id=1),
    )

    todos = await cliente.get("/libros/")
    filtrados = await cliente.get("/libros/", params={"titulo": "rAyUeLa"})
    por_genero = await cliente.get("/libros/", params={"genero_id": 1})

    assert todos.status_code == 200
    assert todos.json()[0] == {
        "id": 1, "isbn": "1", "titulo": "Rayuela", "precio": "25000.00", "stock": 1,
        "editorial": {"id": 1, "nombre": "Sudamericana"}, "genero": {"id": 1, "nombre": "Novela"},
    }
    assert todos.json()[1]["genero"] is None
    assert [libro["id"] for libro in filtrados.json()] == [1, 3]
    assert [libro["id"] for libro in por_genero.json()] == [1]


@pytest.mark.parametrize("texto", ["' OR '1'='1", "%", "_"])
async def test_c08_la_busqueda_usa_parametros_ligados(cliente, catalogo, insertar, texto):
    await insertar(Libro(isbn="1", titulo="Rayuela", precio=Decimal("25000"), stock=1, editorial_id=1))

    respuesta = await cliente.get("/libros/", params={"titulo": texto})

    assert respuesta.status_code == 200
    assert respuesta.json() == []


async def test_listado_de_libros_paginado(cliente, catalogo, insertar):
    await insertar(*[
        Libro(isbn=str(i), titulo=f"Libro {i}", precio=Decimal("100"), stock=1, editorial_id=1)
        for i in range(1, 6)
    ])

    respuesta = await cliente.get("/libros/", params={"limit": 2, "offset": 2})
    fuera_de_rango = await cliente.get("/libros/", params={"limit": 500})

    assert [libro["id"] for libro in respuesta.json()] == [3, 4]
    assert fuera_de_rango.status_code == 422


async def test_c07_el_detalle_usa_una_cantidad_fija_de_consultas(cliente, catalogo, contador):
    await cliente.post("/libros/", json=alta(isbn="A", autores=[{"autor_id": 1, "rol": "autor", "orden": 1}]))
    await cliente.post("/libros/", json=alta(isbn="B", autores=[
        {"autor_id": 1, "rol": "autor", "orden": 1},
        {"autor_id": 2, "rol": "coautor", "orden": 2},
        {"autor_id": 3, "rol": "traductor", "orden": 3},
        {"autor_id": 4, "rol": "ilustrador", "orden": 4},
    ]))

    with contador.contar():
        uno = await cliente.get("/libros/1")
    con_un_autor = contador.cantidad
    with contador.contar():
        cuatro = await cliente.get("/libros/2")
    con_cuatro_autores = contador.cantidad

    assert len(uno.json()["autores"]) == 1
    assert len(cuatro.json()["autores"]) == 4
    assert con_un_autor == con_cuatro_autores == 2


async def test_el_listado_usa_una_cantidad_fija_de_consultas(cliente, catalogo, insertar, contador):
    await insertar(*[
        Libro(isbn=str(i), titulo=f"Libro {i}", precio=Decimal("100"), stock=1, editorial_id=1, genero_id=1)
        for i in range(1, 11)
    ])

    with contador.contar():
        respuesta = await cliente.get("/libros/")

    assert len(respuesta.json()) == 10
    assert contador.cantidad == 1


async def test_patch_parcial_de_libro(cliente, catalogo):
    await cliente.post("/libros/", json=alta())

    respuesta = await cliente.patch("/libros/1", json={"precio": "23500.50", "genero_id": None})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["precio"] == "23500.50"
    assert cuerpo["genero"] is None
    assert cuerpo["titulo"] == "Los que aman, odian"
    assert len(cuerpo["autores"]) == 2


async def test_patch_de_libro_404_409_y_422(cliente, catalogo):
    await cliente.post("/libros/", json=alta(isbn="A"))
    await cliente.post("/libros/", json=alta(isbn="B"))

    inexistente = await cliente.patch("/libros/99", json={"stock": 1})
    isbn_repetido = await cliente.patch("/libros/2", json={"isbn": "A"})
    editorial_inexistente = await cliente.patch("/libros/2", json={"editorial_id": 42})
    stock_negativo = await cliente.patch("/libros/2", json={"stock": -3})
    editorial_nula = await cliente.patch("/libros/2", json={"editorial_id": None})

    assert inexistente.status_code == 404
    assert isbn_repetido.status_code == 409
    assert isbn_repetido.json()["detail"] == "Ya existe un libro con ese ISBN."
    assert editorial_inexistente.status_code == 409
    assert editorial_inexistente.json()["detail"] == "La editorial indicada no existe."
    assert stock_negativo.status_code == 422
    assert editorial_nula.status_code == 422
