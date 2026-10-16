import numpy as np
import pytest
from fastapi.testclient import TestClient

from astraea.model import entrenar, guardar
from astraea.synthetic import generar, generar_paciente


@pytest.fixture(scope="module")
def cliente(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("modelo") / "modelo.joblib"
    guardar(entrenar(generar(500, seed=1), seed=1).bundle, str(ruta))
    import os

    os.environ["ASTRAEA_MODELO"] = str(ruta)
    from api.main import app

    return TestClient(app)


def solicitud(grupo="endo", seed=3):
    perfil, registros = generar_paciente(np.random.default_rng(seed), grupo)
    return {"perfil": perfil, "registros": registros}


def test_salud(cliente):
    assert cliente.get("/salud").json()["estado"] == "ok"


def test_evaluar_devuelve_el_contrato(cliente):
    r = cliente.post("/evaluar", json=solicitud())
    assert r.status_code == 200
    d = r.json()
    assert set(d["alerta"]) == {"nivel", "puntaje"}
    assert set(d["compatibilidad"]) == {"endometriosis", "adenomiosis"}
    assert d["alerta"]["nivel"] in ("alta", "baja")
    assert len(d["patrones"]) <= 3
    assert d["aviso"].startswith("Este resultado no es un diagnóstico")
    assert d["reglas_revisadas_por_profesional"] is False
    assert d["entrenado_con_datos_sinteticos"] is True


def test_edad_fuera_de_rango(cliente):
    s = solicitud()
    s["perfil"]["edad"] = 12
    assert cliente.post("/evaluar", json=s).status_code == 422


def test_pocos_dias_de_registro(cliente):
    s = solicitud()
    s["registros"] = s["registros"][:3]
    assert cliente.post("/evaluar", json=s).status_code == 422


def test_valor_no_permitido(cliente):
    s = solicitud()
    s["registros"][0]["ubic"] = ["Rodilla"]
    assert cliente.post("/evaluar", json=s).status_code == 422


def test_advertencia_con_menos_de_un_ciclo(cliente):
    s = solicitud()
    s["registros"] = s["registros"][:10]
    d = cliente.post("/evaluar", json=s).json()
    assert "advertencia" in d
