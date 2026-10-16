from astraea.rules import estudios_sugeridos, nivel_alerta


def test_alta_por_puntaje_general():
    assert nivel_alerta(0.8, 0.65) == "alta"


def test_alta_por_compatibilidad_aunque_el_puntaje_sea_bajo():
    assert nivel_alerta(0.4, 0.65, p_endo=0.9, p_adeno=0.1) == "alta"


def test_baja():
    assert nivel_alerta(0.2, 0.65, p_endo=0.2, p_adeno=0.3) == "baja"


def test_sin_estudios_si_la_alerta_es_baja():
    assert estudios_sugeridos("baja", 0.9, 0.9) == []


def test_estudios_segun_compatibilidad():
    assert estudios_sugeridos("alta", 0.8, 0.1) == [
        "ecografia_mapeo_pelvico", "resonancia_magnetica", "valoracion_ginecologica"
    ]
    assert estudios_sugeridos("alta", 0.1, 0.8) == ["resonancia_magnetica", "valoracion_ginecologica"]
