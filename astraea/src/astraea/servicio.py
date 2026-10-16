from __future__ import annotations

from typing import Any, Mapping, Sequence

from .explain import factores_principales
from .features import construir_vector
from .model import predecir
from .rules import AVISO, estudios_sugeridos, nivel_alerta
from .schema import DIAS_RECOMENDADOS


def evaluar(
    bundle: dict[str, Any], perfil: Mapping[str, Any], registros: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    vector = construir_vector(perfil, registros)
    p = predecir(bundle, vector)
    nivel = nivel_alerta(p["y_alerta"], bundle["umbral_alerta"], p["y_endo"], p["y_adeno"])
    respuesta: dict[str, Any] = {
        "alerta": {"nivel": nivel, "puntaje": round(p["y_alerta"], 3)},
        "compatibilidad": {
            "endometriosis": round(p["y_endo"], 3),
            "adenomiosis": round(p["y_adeno"], 3),
        },
        "patrones": factores_principales(bundle, vector, k=3),
        "estudios_sugeridos": estudios_sugeridos(nivel, p["y_endo"], p["y_adeno"]),
        "aviso": AVISO,
        "reglas_revisadas_por_profesional": False,
        "entrenado_con_datos_sinteticos": bool(bundle["datos"]["sinteticos"]),
        "version_modelo": bundle["version"],
    }
    if len(registros) < DIAS_RECOMENDADOS:
        respuesta["advertencia"] = (
            f"Se recomiendan al menos {DIAS_RECOMENDADOS} días de registro; "
            f"se recibieron {len(registros)}, así que el resultado es menos confiable."
        )
    return respuesta
