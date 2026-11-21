import copy

import numpy as np
import pytest

from astraea.model import entrenar, guardar
from astraea.reporte import generar_pdf
from astraea.servicio import evaluar
from astraea.synthetic import generar, generar_paciente

# Resultado con la forma del contrato JSON de la sección 6e (alerta alta).
ALTA = {
    "alerta": {"nivel": "alta", "puntaje": 0.605},
    "compatibilidad": {"endometriosis": 0.906, "adenomiosis": 0.138},
    "patrones": [{"factor": "dx_infertilidad", "texto": "Antecedente de infertilidad", "peso": 0.371}],
    "estudios_sugeridos": ["ecografia_mapeo_pelvico", "resonancia_magnetica", "valoracion_ginecologica"],
    "aviso": "Este resultado no es un diagnóstico. Un resultado bajo no descarta la enfermedad.",
    "reglas_revisadas_por_profesional": False,
    "entrenado_con_datos_sinteticos": True,
    "version_modelo": "0.1.0",
}


@pytest.fixture(scope="module")
def bundle():
    return entrenar(generar(500, seed=1), seed=1).bundle


def test_es_un_pdf_valido():
    pdf = generar_pdf(ALTA)
    assert pdf.startswith(b"%PDF-")
    assert pdf.rstrip().endswith(b"%%EOF")
    assert len(pdf) > 2000


def test_incluye_las_secciones_y_los_porcentajes():
    pdf = generar_pdf(ALTA)
    for texto in (b"Reporte Astraea", b"Endometriosis", b"Adenomiosis", b"91 %", b"14 %"):
        assert texto in pdf


def test_porcentaje_redondea_igual_que_la_interfaz():
    # 0,605 es 61 % en la interfaz (Math.round); round() de Python daria 60.
    assert b"61 %" in generar_pdf(ALTA)


def test_alerta_alta_lista_los_estudios():
    pdf = generar_pdf(ALTA)
    assert b"Resonancia" in pdf and b"Ecograf" in pdf


def test_alerta_baja_no_sugiere_estudios():
    baja = copy.deepcopy(ALTA)
    baja["alerta"] = {"nivel": "baja", "puntaje": 0.234}
    baja["estudios_sugeridos"] = []
    pdf = generar_pdf(baja)
    assert b"No se sugieren estudios" in pdf
    assert b"Resonancia" not in pdf


def test_sin_patrones_y_con_advertencia():
    r = copy.deepcopy(ALTA)
    r["patrones"] = []
    r["advertencia"] = "Se recomiendan al menos 28 dias de registro"
    pdf = generar_pdf(r)
    assert b"Ninguno destacado" in pdf
    assert b"Se recomiendan al menos 28" in pdf


def test_resumen_de_registros_es_opcional():
    assert b"Resumen de tus registros" not in generar_pdf(ALTA)
    registros = [{"dolor": 2}, {"dolor": 8}, {"dolor": 5}]
    pdf = generar_pdf(ALTA, registros)
    assert b"Resumen de tus registros" in pdf
    assert b"medio 5.0" in pdf


def test_caracteres_especiales_no_rompen_el_pdf():
    r = copy.deepcopy(ALTA)
    r["patrones"] = [{"factor": "x", "texto": "Dolor <fuerte> & constante", "peso": 0.1}]
    assert generar_pdf(r).startswith(b"%PDF-")


def test_con_el_resultado_real_del_servicio(bundle):
    perfil, registros = generar_paciente(np.random.default_rng(3), "endo")
    resultado = evaluar(bundle, perfil, registros)
    pdf = generar_pdf(resultado, registros)
    assert pdf.startswith(b"%PDF-") and b"Endometriosis" in pdf


# --- Endpoint POST /reporte: se prueba solo cuando api/main.py ya lo tiene (lo agrega Natalia) ---
def _app():
    from api.main import app

    return app


def _tiene_endpoint():
    try:
        return any(getattr(r, "path", "") == "/reporte" for r in _app().routes)
    except Exception:
        return False


necesita_endpoint = pytest.mark.skipif(not _tiene_endpoint(), reason="api/main.py todavía no tiene POST /reporte")


@pytest.fixture(scope="module")
def cliente(tmp_path_factory, bundle):
    import os

    from fastapi.testclient import TestClient

    ruta = tmp_path_factory.mktemp("modelo") / "modelo.joblib"
    guardar(bundle, str(ruta))
    os.environ["ASTRAEA_MODELO"] = str(ruta)
    return TestClient(_app())


def _solicitud(seed=3):
    perfil, registros = generar_paciente(np.random.default_rng(seed), "endo")
    return {"perfil": perfil, "registros": registros}


@necesita_endpoint
def test_endpoint_devuelve_un_pdf(cliente):
    r = cliente.post("/reporte", json=_solicitud())
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert "attachment" in r.headers["content-disposition"]
    assert r.content.startswith(b"%PDF-")


@necesita_endpoint
def test_endpoint_valida_las_entradas(cliente):
    s = _solicitud()
    s["perfil"]["edad"] = 12
    assert cliente.post("/reporte", json=s).status_code == 422
    s = _solicitud()
    s["registros"] = s["registros"][:3]
    assert cliente.post("/reporte", json=s).status_code == 422
