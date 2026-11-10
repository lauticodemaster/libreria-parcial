"""Comprobaciones estáticas de la imagen (Ejercicio 7).

No necesitan Docker ni base de datos: leen el Dockerfile y el .dockerignore y verifican
lo que pide la consigna. Lo que sólo se ve con Docker corriendo (healthy, docker logs,
id del proceso) son los casos D, que se demuestran en el VPS.
"""

from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
DOCKERFILE = (RAIZ / "Dockerfile").read_text(encoding="utf-8")
IGNORADOS = {
    linea.strip()
    for linea in (RAIZ / ".dockerignore").read_text(encoding="utf-8").splitlines()
    if linea.strip() and not linea.lstrip().startswith("#")
}
INSTRUCCIONES = [
    linea.strip()
    for linea in DOCKERFILE.splitlines()
    if linea.strip() and not linea.lstrip().startswith("#")
]


def indice_de(prefijo: str) -> int:
    return next(i for i, linea in enumerate(INSTRUCCIONES) if linea.startswith(prefijo))


def test_parte_de_python_312_alpine():
    assert INSTRUCCIONES[0] == "FROM python:3.12-alpine"


def test_instala_requirements_antes_de_copiar_el_codigo_y_sin_cache():
    copia_requirements = indice_de("COPY requirements.txt")
    instalacion = indice_de("RUN pip install")
    copia_codigo = indice_de("COPY --chown=libreria:libreria app")

    assert copia_requirements < instalacion < copia_codigo
    assert "--no-cache-dir" in INSTRUCCIONES[instalacion]


def test_no_corre_como_root():
    usuario = [linea for linea in INSTRUCCIONES if linea.startswith("USER ")]

    assert usuario == ["USER libreria"]
    assert indice_de("USER ") < indice_de("CMD ")


def test_healthcheck_con_wget_a_127_0_0_1():
    assert "wget -qO- http://127.0.0.1:8000/health/ready" in DOCKERFILE
    assert "localhost" not in DOCKERFILE.split("HEALTHCHECK", 1)[1].split("CMD [", 1)[0]


def test_uvicorn_escucha_en_0_0_0_0():
    assert INSTRUCCIONES[-1] == 'CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]'


def test_el_dockerfile_no_trae_direccion_de_base_ni_secretos():
    assert "DATABASE_URL" not in DOCKERFILE
    assert "postgresql" not in DOCKERFILE.lower()


@pytest.mark.parametrize("ruta", [".env", ".venv/", ".git/", "**/__pycache__/"])
def test_el_dockerignore_excluye_secretos_y_archivos_generados(ruta):
    assert ruta in IGNORADOS


@pytest.mark.parametrize(
    "ruta",
    [
        "openspec/", "knowledge-base/", "docs/", "discovery/", ".claude/", ".atl/",
        ".active-orchestrator-state.json", "skills-lock.json", "CHANGES.md", "AGENTS.md", "CLAUDE.md", "DEPLOY.md",
        "*.md",
    ],
)
def test_el_dockerignore_excluye_los_artefactos_opsx_y_la_kb(ruta):
    assert ruta in IGNORADOS
