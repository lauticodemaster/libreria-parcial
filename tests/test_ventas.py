import asyncio
import logging
from decimal import Decimal

import pytest
from sqlmodel import update

from app.modules.clientes.models import Cliente
from app.modules.editoriales.models import Editorial
from app.modules.libros.models import Libro
from app.modules.ventas import service

pytestmark = pytest.mark.anyio


@pytest.fixture
async def datos(insertar):
    """Clientes 1 y 2, libros 1 a 4 (precios 25000, 18000, 22000 y 27000)."""
    editorial = Editorial(nombre="Sudamericana", pais="Argentina")
    await insertar(editorial)
    await insertar(
        Cliente(nombre="Ana Pérez", email="ana@example.com"),
        Cliente(nombre="Tomás Ríos", email="tomas@example.com"),
        Libro(isbn="1", titulo="Rayuela", precio=Decimal("25000.00"), stock=10, editorial_id=editorial.id),
        Libro(isbn="2", titulo="Bestiario", precio=Decimal("18000.00"), stock=10, editorial_id=editorial.id),
        Libro(isbn="3", titulo="La invención de Morel", precio=Decimal("22000.00"), stock=10,
              editorial_id=editorial.id),
        Libro(isbn="4", titulo="Respiración artificial", precio=Decimal("27000.00"), stock=10,
              editorial_id=editorial.id),
    )


@pytest.fixture
def sin_espera(monkeypatch):
    """El aviso espera 0,5 s; en las pruebas de la API no hace falta esperar."""
    original = asyncio.sleep
    monkeypatch.setattr(service.asyncio, "sleep", lambda segundos: original(0))


VENTA = {"cliente_id": 2, "renglones": [{"libro_id": 1, "cantidad": 2}, {"libro_id": 4, "cantidad": 1}]}


async def test_c06_venta_valida_copia_precios_y_calcula_el_total(cliente, datos, sin_espera):
    respuesta = await cliente.post("/ventas/", json=VENTA)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["id"] == 1
    assert cuerpo["fecha"].endswith("Z")
    assert cuerpo["total"] == "77000.00"
    assert cuerpo["cliente"] == {"id": 2, "nombre": "Tomás Ríos", "email": "tomas@example.com"}
    assert cuerpo["renglones"] == [
        {"libro_id": 1, "titulo": "Rayuela", "cantidad": 2, "precio_unitario": "25000.00", "subtotal": "50000.00"},
        {"libro_id": 4, "titulo": "Respiración artificial", "cantidad": 1, "precio_unitario": "27000.00",
         "subtotal": "27000.00"},
    ]


async def test_el_precio_del_renglon_no_cambia_si_cambia_el_libro(cliente, datos, aplicacion, sin_espera):
    await cliente.post("/ventas/", json=VENTA)
    async with aplicacion.state.fabrica_sesiones() as sesion:
        await sesion.exec(update(Libro).where(Libro.id == 1).values(precio=Decimal("99999.00")))
        await sesion.commit()

    detalle = await cliente.get("/ventas/1")

    assert detalle.json()["renglones"][0]["precio_unitario"] == "25000.00"
    assert detalle.json()["total"] == "77000.00"


async def test_c05_libro_inexistente_responde_409(cliente, datos, sin_espera):
    respuesta = await cliente.post(
        "/ventas/", json={"cliente_id": 1, "renglones": [{"libro_id": 1, "cantidad": 1}, {"libro_id": 999, "cantidad": 1}]}
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "No existe el libro con id 999."
    assert (await cliente.get("/ventas/")).json() == []


async def test_c05_cliente_inexistente_responde_409(cliente, datos, sin_espera):
    respuesta = await cliente.post("/ventas/", json={"cliente_id": 999, "renglones": [{"libro_id": 1, "cantidad": 1}]})

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == "El cliente indicado no existe."


@pytest.mark.parametrize(
    "cuerpo",
    [
        {"cliente_id": 1, "renglones": []},
        {"cliente_id": 1},
        {"cliente_id": 1, "renglones": [{"libro_id": 1, "cantidad": 0}]},
        {"cliente_id": 1, "renglones": [{"libro_id": 1, "cantidad": 1}, {"libro_id": 1, "cantidad": 2}]},
        {"cliente_id": 1, "renglones": [{"libro_id": 1, "cantidad": 1, "precio_unitario": "1.00"}]},
        {"cliente_id": 1, "total": "1.00", "renglones": [{"libro_id": 1, "cantidad": 1}]},
        {"cliente_id": 1, "fecha": "2020-01-01T00:00:00Z", "renglones": [{"libro_id": 1, "cantidad": 1}]},
    ],
)
async def test_venta_que_no_cumple_el_contrato_responde_422(cliente, datos, cuerpo):
    respuesta = await cliente.post("/ventas/", json=cuerpo)

    assert respuesta.status_code == 422


async def test_las_ventas_no_se_modifican(cliente, datos, sin_espera):
    await cliente.post("/ventas/", json=VENTA)

    assert (await cliente.patch("/ventas/1", json={"cliente_id": 1})).status_code == 405
    assert (await cliente.delete("/ventas/1")).status_code == 405


async def test_detalle_404_y_422(cliente):
    assert (await cliente.get("/ventas/5")).status_code == 404
    assert (await cliente.get("/ventas/cinco")).status_code == 422


async def test_listado_de_ventas_paginado(cliente, datos, sin_espera):
    for cantidad in (1, 2, 3):
        await cliente.post("/ventas/", json={"cliente_id": 1, "renglones": [{"libro_id": 2, "cantidad": cantidad}]})

    respuesta = await cliente.get("/ventas/", params={"limit": 2, "offset": 1})

    assert respuesta.status_code == 200
    assert [(v["id"], v["total"]) for v in respuesta.json()] == [(2, "36000.00"), (3, "54000.00")]
    assert respuesta.json()[0]["cliente"]["nombre"] == "Ana Pérez"
    assert (await cliente.get("/ventas/", params={"limit": 0})).status_code == 422


async def test_c07_el_detalle_de_venta_usa_una_cantidad_fija_de_consultas(cliente, datos, contador, sin_espera):
    await cliente.post("/ventas/", json={"cliente_id": 1, "renglones": [{"libro_id": 1, "cantidad": 1}]})
    await cliente.post("/ventas/", json={"cliente_id": 2, "renglones": [
        {"libro_id": 1, "cantidad": 1}, {"libro_id": 2, "cantidad": 2},
        {"libro_id": 3, "cantidad": 3}, {"libro_id": 4, "cantidad": 4},
    ]})

    with contador.contar():
        una = await cliente.get("/ventas/1")
    con_un_renglon = contador.cantidad
    with contador.contar():
        cuatro = await cliente.get("/ventas/2")
    con_cuatro_renglones = contador.cantidad

    assert len(una.json()["renglones"]) == 1
    assert len(cuatro.json()["renglones"]) == 4
    assert con_un_renglon == con_cuatro_renglones == 2


async def test_el_aviso_del_comprobante_corre_en_segundo_plano(cliente, datos, monkeypatch):
    esperas: list[float] = []
    original = asyncio.sleep

    async def sleep_registrado(segundos):
        esperas.append(segundos)
        await original(0)

    monkeypatch.setattr(service.asyncio, "sleep", sleep_registrado)
    mensajes: list[str] = []
    manejador = logging.Handler()
    manejador.emit = lambda registro: mensajes.append(registro.getMessage())
    logging.getLogger("libreria.ventas").addHandler(manejador)
    try:
        respuesta = await cliente.post("/ventas/", json=VENTA)
    finally:
        logging.getLogger("libreria.ventas").removeHandler(manejador)

    assert respuesta.status_code == 201
    assert esperas == [0.5]
    assert mensajes == ["Comprobante de la venta 1 enviado a tomas@example.com (total $77000.00)."]


async def test_el_aviso_no_bloquea_al_servidor():
    """Mientras corre el aviso (await asyncio.sleep), el bucle atiende otras tareas."""
    aviso = asyncio.create_task(service.avisar_comprobante(1, "ana@example.com", Decimal("10.00")))
    await asyncio.sleep(0)
    otra_tarea_terminada = await asyncio.wait_for(asyncio.sleep(0, result=True), timeout=0.1)

    assert otra_tarea_terminada is True
    assert not aviso.done()
    await aviso
