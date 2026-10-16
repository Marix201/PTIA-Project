"""
Un registro diario tiene la forma:
    {"dolor": 0-10, "ubic": [...], "tipo": [...], "en_periodo": bool,
     "sangrado": 0-4, "fatiga": 0-10, "gi": [...]}
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

from .schema import DIAS_RECOMENDADOS, FEATURES, SINTOMAS_GI_URIN

DOLOR_ALTO = 7  
DOLOR_FUERA_PERIODO = 3  
SANGRADO_ABUNDANTE = 4

_GI = {"Hinchazón", "Diarrea o estreñimiento", "Dolor al evacuar"}
_URIN = {"Dolor al orinar", "Urgencia urinaria"}
assert _GI | _URIN == set(SINTOMAS_GI_URIN)


def perfil_a_variables(perfil: Mapping[str, Any]) -> dict[str, float]:
    """Variables del perfil. Un laboratorio ausente queda como NaN más un indicador."""
    fam = perfil.get("fam", "nose")
    dx = set(perfil.get("dx", []))
    med = set(perfil.get("med", []))
    ca125 = perfil.get("ca125")
    tiene_ca = ca125 is not None and not (isinstance(ca125, float) and math.isnan(ca125))

    return {
        "fam_primer_grado": {"si": 1.0, "no": 0.0, "otro": 0.0}.get(fam, math.nan),
        "fam_otro": 1.0 if fam == "otro" else 0.0,
        "dx_sop": float("SOP" in dx),
        "dx_miomas": float("Miomas" in dx),
        "dx_infertilidad": float("Infertilidad" in dx),
        "dx_eii": float("Enfermedad inflamatoria intestinal" in dx),
        "dx_otro": float("Otro" in dx),
        "edad": float(perfil["edad"]),
        "menarquia_edad": float(perfil["menarquia_edad"]),
        "med_hormonal": float("Hormonal" in med),
        "med_antiinflamatorio": float("Antiinflamatorio" in med),
        "med_analgesico": float("Analgésico" in med),
        "ca125": float(ca125) if tiene_ca else math.nan,
        "ca125_faltante": 0.0 if tiene_ca else 1.0,
    }


def diario_a_variables(registros: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    """Resume 1 a 2 ciclos de registro diario en variables comparables entre pacientes."""
    n = len(registros)
    if n == 0:
        raise ValueError("Se necesita al menos un registro diario.")

    dolores = [r["dolor"] for r in registros]
    dias_dolor = [r for r in registros if r["dolor"] >= 1]
    fuera = [r for r in registros if not r["en_periodo"]]

    def frac(items, cond, base):
        return sum(1 for x in items if cond(x)) / base if base else 0.0

    n_dolor = len(dias_dolor)
    out = {
        "dolor_medio": sum(dolores) / n,
        "dolor_max": float(max(dolores)),
        "pct_dias_dolor_alto": frac(registros, lambda r: r["dolor"] >= DOLOR_ALTO, n),
        "pct_dolor_en_periodo": frac(dias_dolor, lambda r: r["en_periodo"], n_dolor),
        "pct_dias_fuera_periodo_con_dolor": frac(
            fuera, lambda r: r["dolor"] >= DOLOR_FUERA_PERIODO, len(fuera)
        ),
        "pct_dias_sangrado_abundante": frac(registros, lambda r: r["sangrado"] >= SANGRADO_ABUNDANTE, n),
        # normalizado a una ventana de 28 días para que sea comparable
        "dias_con_sangrado": sum(1 for r in registros if r["sangrado"] >= 1) * DIAS_RECOMENDADOS / n,
        "fatiga_media": sum(r["fatiga"] for r in registros) / n,
        "pct_dias_gi": frac(registros, lambda r: bool(_GI & set(r.get("gi", []))), n),
        "pct_dias_urinario": frac(registros, lambda r: bool(_URIN & set(r.get("gi", []))), n),
    }
    for clave, nombre in (
        ("loc_pelvico", "Pélvico"),
        ("loc_lumbar", "Lumbar"),
        ("loc_relaciones", "Durante relaciones"),
        ("loc_evacuar", "Al evacuar"),
    ):
        out[clave] = frac(dias_dolor, lambda r, nombre=nombre: nombre in r.get("ubic", []), n_dolor)
    for clave, nombre in (
        ("tipo_colico", "Cólico"),
        ("tipo_punzante", "Punzante"),
        ("tipo_quemante", "Quemante"),
        ("tipo_sordo", "Sordo"),
    ):
        out[clave] = frac(dias_dolor, lambda r, nombre=nombre: nombre in r.get("tipo", []), n_dolor)
    return out


def construir_vector(
    perfil: Mapping[str, Any], registros: Sequence[Mapping[str, Any]]
) -> dict[str, float]:
    """Vector completo, en el orden de schema.FEATURES."""
    todas = {**perfil_a_variables(perfil), **diario_a_variables(registros)}
    return {nombre: todas[nombre] for nombre in FEATURES}
