"""Generador de datos SINTÉTICOS para validar el pipeline de Astraea.

IMPORTANTE: estos datos NO son pacientes reales. Los parámetros de abajo son SUPUESTOS pensados para que el modelo tenga algo que
aprender y para que los grupos se solapen, como ocurre en la práctica. 

Cada paciente se simula como un registro diario de 14 a 56 días más su perfil; luego se
convierte en variables con features.py, igual que hará la API con datos reales.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .features import construir_vector
from .schema import (
    DX_PREVIOS,
    SINTOMAS_GI_URIN,
    TARGETS,
)

GRUPOS = ("otra", "endo", "adeno", "ambas")
PROPORCIONES = (0.40, 0.25, 0.20, 0.15)

# Parámetros por grupo, en el orden de GRUPOS.
P = {
    "dolor_periodo": (2.5, 6.0, 5.5, 6.5),       # media del dolor en días de periodo
    "p_dolor_fuera": (0.10, 0.40, 0.20, 0.40),   # prob. de dolor un día fuera del periodo
    "dolor_fuera": (2.0, 4.5, 3.5, 4.5),         # intensidad media de ese dolor
    "p_abundante": (0.12, 0.20, 0.55, 0.55),     # prob. de sangrado abundante en día de periodo
    "fatiga": (3.0, 5.5, 4.5, 5.5),
    "p_gi": (0.08, 0.30, 0.12, 0.30),
    "p_urin": (0.04, 0.12, 0.05, 0.12),
    "loc_lumbar": (0.20, 0.40, 0.35, 0.40),
    "loc_relaciones": (0.05, 0.30, 0.12, 0.30),
    "loc_evacuar": (0.04, 0.30, 0.08, 0.30),
    "p_fam_si": (0.06, 0.30, 0.12, 0.30),
    "p_fam_otro": (0.08, 0.20, 0.10, 0.20),
    "p_miomas": (0.05, 0.05, 0.20, 0.20),
    "p_infertilidad": (0.05, 0.25, 0.20, 0.30),
    "p_eii": (0.03, 0.06, 0.03, 0.06),
    "edad_media": (29, 31, 38, 35),
    "ca125_mediana": (15, 35, 22, 38),
}
TIPOS = {"Cólico": 0.55, "Punzante": 0.25, "Quemante": 0.08, "Sordo": 0.32}
P_CA125_DISPONIBLE = 0.12
RUIDO_PERIODO = 0.08  # prob. de que la usuaria marque mal si el dolor coincide con el periodo


def _g(clave: str, i: int) -> float:
    return P[clave][i]


def _clip_int(x: float, lo: int, hi: int) -> int:
    return int(min(hi, max(lo, round(x))))


def generar_paciente(rng: np.random.Generator, grupo: str) -> tuple[dict, list[dict]]:
    """Devuelve (perfil, registros_diarios) de una paciente simulada del grupo indicado."""
    i = GRUPOS.index(grupo)

    # perfil
    r = rng.random()
    if r < _g("p_fam_si", i):
        fam = "si"
    elif r < _g("p_fam_si", i) + _g("p_fam_otro", i):
        fam = "otro"
    elif r < _g("p_fam_si", i) + _g("p_fam_otro", i) + 0.05:
        fam = "nose"
    else:
        fam = "no"
    dx = []
    if rng.random() < 0.10:
        dx.append("SOP")
    if rng.random() < _g("p_miomas", i):
        dx.append("Miomas")
    if rng.random() < _g("p_infertilidad", i):
        dx.append("Infertilidad")
    if rng.random() < _g("p_eii", i):
        dx.append("Enfermedad inflamatoria intestinal")
    if rng.random() < 0.10:
        dx.append("Otro")
    assert set(dx) <= set(DX_PREVIOS)
    en_endo = grupo in ("endo", "ambas")
    med = []
    if rng.random() < (0.40 if en_endo else 0.25):
        med.append("Hormonal")
    if rng.random() < (0.60 if grupo != "otra" else 0.30):
        med.append("Antiinflamatorio")
    if rng.random() < (0.70 if grupo != "otra" else 0.40):
        med.append("Analgésico")
    ca125 = None
    if rng.random() < P_CA125_DISPONIBLE:
        ca125 = round(float(rng.lognormal(np.log(_g("ca125_mediana", i)), 0.5)), 1)
    perfil = {
        "fam": fam,
        "dx": dx,
        "med": med,
        "ca125": ca125,
        "edad": _clip_int(rng.normal(_g("edad_media", i), 6.5), 18, 55),
        "menarquia_edad": _clip_int(rng.normal(12.2 if en_endo else 12.8, 1.3), 8, 18),
    }

    # registro diario
    # una paciente con la enfermedad puede
    # tener síntomas leves (w < 1) y una paciente sin ella puede tener síntomas parecidos
    # (dismenorrea primaria u otras causas), con un 30 % de probabilidad.
    if grupo == "otra":
        if rng.random() < 0.30:
            i_s, w = int(rng.choice([1, 2])), float(rng.beta(2, 3))
        else:
            i_s, w = 0, 0.0
    else:
        i_s, w = i, float(rng.beta(3, 2))

    def s(clave: str) -> float:
        base = P[clave][0]
        return base + w * (P[clave][i_s] - base)

    n_dias = int(rng.choice([14, 28, 28, 42, 56]))
    largo_periodo = _clip_int(rng.normal(5 + (1 if grupo in ("adeno", "ambas") else 0), 1.0), 3, 8)
    mu_periodo = s("dolor_periodo") + rng.normal(0, 1.2)  # variación entre pacientes
    mu_fatiga = s("fatiga") + rng.normal(0, 1.0)
    registros = []
    for dia in range(n_dias):
        real_periodo = (dia % 28) < largo_periodo
        if real_periodo:
            dolor = _clip_int(rng.normal(mu_periodo, 2.0), 0, 10)
            if rng.random() < s("p_abundante"):
                sangrado = 4
            else:
                sangrado = int(rng.choice([1, 2, 3], p=[0.25, 0.4, 0.35]))
        else:
            dolor = (
                _clip_int(rng.normal(s("dolor_fuera"), 1.5), 1, 10)
                if rng.random() < s("p_dolor_fuera")
                else 0
            )
            sangrado = 1 if rng.random() < 0.03 else 0

        ubic, tipo = [], []
        if dolor >= 1:
            if rng.random() < 0.9:
                ubic.append("Pélvico")
            if rng.random() < s("loc_lumbar"):
                ubic.append("Lumbar")
            if rng.random() < s("loc_relaciones"):
                ubic.append("Durante relaciones")
            if rng.random() < s("loc_evacuar"):
                ubic.append("Al evacuar")
            tipo = [t for t, p in TIPOS.items() if rng.random() < p]
        gi = []
        if rng.random() < s("p_gi"):
            gi.append(str(rng.choice(["Hinchazón", "Diarrea o estreñimiento", "Dolor al evacuar"])))
        if rng.random() < s("p_urin"):
            gi.append(str(rng.choice(["Dolor al orinar", "Urgencia urinaria"])))
        assert set(gi) <= set(SINTOMAS_GI_URIN)

        reporta_periodo = real_periodo if rng.random() > RUIDO_PERIODO else (not real_periodo)
        registros.append(
            {
                "dolor": dolor,
                "ubic": ubic,
                "tipo": tipo,
                "en_periodo": bool(reporta_periodo),
                "sangrado": sangrado,
                "fatiga": _clip_int(rng.normal(mu_fatiga, 2.0), 0, 10),
                "gi": gi,
            }
        )
    return perfil, registros


def generar(n: int = 2000, seed: int = 42) -> pd.DataFrame:
    """Conjunto sintético con las variables del modelo, el grupo y las tres etiquetas."""
    rng = np.random.default_rng(seed)
    grupos = rng.choice(GRUPOS, size=n, p=PROPORCIONES)
    filas = []
    for g in grupos:
        perfil, registros = generar_paciente(rng, str(g))
        fila = construir_vector(perfil, registros)
        fila["grupo"] = str(g)
        filas.append(fila)
    df = pd.DataFrame(filas)
    df["y_endo"] = df["grupo"].isin(["endo", "ambas"]).astype(int)
    df["y_adeno"] = df["grupo"].isin(["adeno", "ambas"]).astype(int)
    df["y_alerta"] = (df["grupo"] != "otra").astype(int)
    assert all(t in df.columns for t in TARGETS)
    return df
