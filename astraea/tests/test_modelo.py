import pytest

from astraea.model import ece, elegir_umbral, entrenar, predecir, sens_espec
from astraea.schema import FEATURES, TARGETS
from astraea.synthetic import generar


@pytest.fixture(scope="module")
def resultado():
    return entrenar(generar(500, seed=1), seed=1)


def test_metricas_razonables(resultado):
    m = resultado.metricas["y_alerta"]
    assert m["auc"] > 0.75
    assert 0 <= m["brier"] <= 0.25


def test_bundle_completo(resultado):
    b = resultado.bundle
    assert set(b["modelos"]) == set(TARGETS)
    assert b["features"] == FEATURES
    assert b["datos"]["sinteticos"] is True


def test_probabilidades_independientes(resultado):
    df = generar(20, seed=5)
    vector = df.iloc[0][FEATURES].to_dict()
    p = predecir(resultado.bundle, vector)
    assert all(0.0 <= p[t] <= 1.0 for t in TARGETS)


def test_umbral_cumple_sensibilidad():
    import numpy as np

    y = np.array([1, 1, 1, 1, 0, 0, 0, 0])
    p = np.array([0.9, 0.8, 0.6, 0.3, 0.5, 0.2, 0.1, 0.05])
    u = elegir_umbral(y, p, sens_min=0.75)
    assert sens_espec(y, p, u)[0] >= 0.75


def test_ece_perfecta():
    import numpy as np

    assert ece(np.array([0, 1]), np.array([0.0, 1.0])) == 0.0
