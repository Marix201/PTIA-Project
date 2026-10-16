import math

import pytest

from astraea.features import construir_vector, diario_a_variables, perfil_a_variables
from astraea.schema import FEATURES


def dia(dolor=0, en_periodo=False, sangrado=0, fatiga=0, ubic=(), tipo=(), gi=()):
    return {
        "dolor": dolor, "en_periodo": en_periodo, "sangrado": sangrado, "fatiga": fatiga,
        "ubic": list(ubic), "tipo": list(tipo), "gi": list(gi),
    }


def test_resumen_del_diario():
    regs = [
        dia(dolor=8, en_periodo=True, sangrado=4, fatiga=6, ubic=["Pélvico"], tipo=["Cólico"]),
        dia(dolor=6, en_periodo=True, sangrado=2, fatiga=4, ubic=["Pélvico", "Lumbar"], tipo=["Cólico"], gi=["Hinchazón"]),
        dia(dolor=4, en_periodo=False, sangrado=0, fatiga=2, ubic=["Pélvico"], tipo=["Punzante"], gi=["Dolor al orinar"]),
        dia(dolor=0, en_periodo=False, sangrado=0, fatiga=0),
    ]
    v = diario_a_variables(regs)
    assert v["dolor_medio"] == pytest.approx(4.5)
    assert v["dolor_max"] == 8
    assert v["pct_dias_dolor_alto"] == pytest.approx(0.25)          # solo el día con dolor 8
    assert v["pct_dolor_en_periodo"] == pytest.approx(2 / 3)         # 2 de 3 días con dolor
    assert v["pct_dias_fuera_periodo_con_dolor"] == pytest.approx(0.5)  # 1 de 2 días fuera del periodo
    assert v["pct_dias_sangrado_abundante"] == pytest.approx(0.25)
    assert v["dias_con_sangrado"] == pytest.approx(2 * 28 / 4)       # normalizado a 28 días
    assert v["pct_dias_gi"] == pytest.approx(0.25)
    assert v["pct_dias_urinario"] == pytest.approx(0.25)
    assert v["loc_lumbar"] == pytest.approx(1 / 3)
    assert v["tipo_colico"] == pytest.approx(2 / 3)


def test_diario_vacio_falla():
    with pytest.raises(ValueError):
        diario_a_variables([])


def test_perfil_laboratorio_opcional():
    base = {"fam": "si", "dx": ["Miomas"], "med": ["Hormonal"], "edad": 30, "menarquia_edad": 12}
    sin = perfil_a_variables({**base, "ca125": None})
    con = perfil_a_variables({**base, "ca125": 40.0})
    assert math.isnan(sin["ca125"]) and sin["ca125_faltante"] == 1.0
    assert con["ca125"] == 40.0 and con["ca125_faltante"] == 0.0
    assert sin["fam_primer_grado"] == 1.0 and sin["dx_miomas"] == 1.0 and sin["med_hormonal"] == 1.0


def test_fam_no_se_es_dato_faltante():
    v = perfil_a_variables({"fam": "nose", "edad": 30, "menarquia_edad": 12})
    assert math.isnan(v["fam_primer_grado"])


def test_vector_completo_en_orden():
    perfil = {"fam": "no", "edad": 25, "menarquia_edad": 13}
    v = construir_vector(perfil, [dia(dolor=3, en_periodo=True, ubic=["Pélvico"])])
    assert list(v) == FEATURES
