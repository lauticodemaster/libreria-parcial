from decimal import Decimal

import pytest

from app.modules.clientes.models import Cliente
from app.modules.ventas.models import Venta

pytestmark = pytest.mark.anyio


async def test_alta_de_cliente(cliente):
    respuesta = await cliente.post("/clientes/", json={"nombre": "Tomás Ríos", "email": "tomas@example.com"})

    assert respuesta.status_code == 201
    assert respuesta.json() == {"id": 1, "nombre": "Tomás Ríos", "email": "tomas@example.com"}


async def test_c02_email_repetido_responde_409_con_mensaje_propio(cliente):
    await cliente.post("/clientes/", json={"nombre": "Ana", "email": "ana@example.com"})

    respuesta = await cliente.post("/clientes/", json={"nombre": "Ana Pérez", "email": "ana@example.com"})

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "Ya existe un cliente con ese email."


async def test_email_invalido_responde_422(cliente):
    respuesta = await cliente.post("/clientes/", json={"nombre": "Ana", "email": "no-es-un-email"})

    assert respuesta.status_code == 422


async def test_detalle_con_perfil_vacio_y_luego_con_perfil(cliente):
    await cliente.post("/clientes/", json={"nombre": "Ana", "email": "ana@example.com"})

    sin_perfil = await cliente.get("/clientes/1")
    alta_perfil = await cliente.post(
        "/clientes/1/perfil", json={"telefono": "11 4444-5555", "direccion": "Av. Corrientes 1234"}
    )
    con_perfil = await cliente.get("/clientes/1")

    assert sin_perfil.status_code == 200
    assert sin_perfil.json()["perfil"] is None
    assert alta_perfil.status_code == 201
    assert alta_perfil.json() == {
        "id": 1, "cliente_id": 1, "telefono": "11 4444-5555", "direccion": "Av. Corrientes 1234"
    }
    # Cliente.perfil es un objeto, no una lista.
    assert con_perfil.json()["perfil"] == alta_perfil.json()


async def test_c03_segundo_perfil_para_el_mismo_cliente_responde_409(cliente):
    await cliente.post("/clientes/", json={"nombre": "Ana", "email": "ana@example.com"})
    perfil = {"telefono": "11 4444-5555", "direccion": "Av. Corrientes 1234"}
    await cliente.post("/clientes/1/perfil", json=perfil)

    respuesta = await cliente.post("/clientes/1/perfil", json=perfil)

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "El cliente ya tiene un perfil cargado."


async def test_perfil_de_cliente_inexistente_responde_404(cliente):
    respuesta = await cliente.post("/clientes/77/perfil", json={"telefono": "123456", "direccion": "Calle 1"})

    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "El cliente no existe."


async def test_cliente_inexistente_404_y_no_entero_422(cliente):
    assert (await cliente.get("/clientes/5")).status_code == 404
    assert (await cliente.get("/clientes/cinco")).status_code == 422


async def test_patch_parcial_de_cliente_y_errores(cliente):
    await cliente.post("/clientes/", json={"nombre": "Ana", "email": "ana@example.com"})
    await cliente.post("/clientes/", json={"nombre": "Tomás", "email": "tomas@example.com"})

    parcial = await cliente.patch("/clientes/1", json={"nombre": "Ana Pérez"})
    repetido = await cliente.patch("/clientes/2", json={"email": "ana@example.com"})
    invalido = await cliente.patch("/clientes/2", json={"email": "x"})
    inexistente = await cliente.patch("/clientes/9", json={"nombre": "Nadie"})

    assert parcial.status_code == 200
    assert parcial.json() == {"id": 1, "nombre": "Ana Pérez", "email": "ana@example.com", "perfil": None}
    assert repetido.status_code == 409
    assert invalido.status_code == 422
    assert inexistente.status_code == 404


async def test_ventas_del_cliente(cliente, insertar):
    ana, tomas = Cliente(nombre="Ana", email="ana@example.com"), Cliente(nombre="Tomás", email="t@example.com")
    await insertar(ana, tomas)
    await insertar(
        Venta(cliente_id=ana.id, total=Decimal("100.00")),
        Venta(cliente_id=tomas.id, total=Decimal("50.00")),
        Venta(cliente_id=ana.id, total=Decimal("75.50")),
    )

    respuesta = await cliente.get(f"/clientes/{ana.id}/ventas")
    inexistente = await cliente.get("/clientes/99/ventas")

    assert respuesta.status_code == 200
    assert [(v["id"], v["total"]) for v in respuesta.json()] == [(1, "100.00"), (3, "75.50")]
    assert "fecha" in respuesta.json()[0]
    assert inexistente.status_code == 404
