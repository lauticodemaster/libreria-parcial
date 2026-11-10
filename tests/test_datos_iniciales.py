import pytest

from app import seed

pytestmark = pytest.mark.anyio


async def test_los_datos_iniciales_dejan_un_estado_conocido(cliente, aplicacion):
    await seed.cargar(aplicacion.state.motor)
    await seed.cargar(aplicacion.state.motor)  # se puede correr más de una vez

    libros = await cliente.get("/libros/")
    tomas = await cliente.get("/clientes/2")
    ana = await cliente.get("/clientes/1")
    ventas = await cliente.get("/ventas/")

    assert len(libros.json()) == 6
    assert libros.json()[0]["titulo"] == "Rayuela"
    assert libros.json()[3]["titulo"] == "Respiración artificial"
    assert tomas.json() == {"id": 2, "nombre": "Tomás Ríos", "email": "tomas@example.com", "perfil": None}
    assert ana.json()["perfil"] is not None
    assert [v["id"] for v in ventas.json()] == [1]


async def test_con_los_datos_iniciales_el_ejemplo_de_la_consigna_da_77000(cliente, aplicacion):
    await seed.cargar(aplicacion.state.motor)

    respuesta = await cliente.post(
        "/ventas/",
        json={"cliente_id": 2, "renglones": [{"libro_id": 1, "cantidad": 2}, {"libro_id": 4, "cantidad": 1}]},
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["id"] == 2
    assert respuesta.json()["total"] == "77000.00"


async def test_con_los_datos_iniciales_el_alta_de_libro_de_la_consigna_funciona(cliente, aplicacion):
    await seed.cargar(aplicacion.state.motor)

    respuesta = await cliente.post("/libros/", json={
        "isbn": "978-950-00-0006-6", "titulo": "Los que aman, odian", "precio": "21000.00", "stock": 4,
        "editorial_id": 1, "genero_id": 1,
        "autores": [{"autor_id": 3, "rol": "coautor", "orden": 1}, {"autor_id": 4, "rol": "coautor", "orden": 2}],
    })

    assert respuesta.status_code == 201
    assert [a["nombre"] for a in respuesta.json()["autores"]] == ["Adolfo Bioy Casares", "Silvina Ocampo"]
