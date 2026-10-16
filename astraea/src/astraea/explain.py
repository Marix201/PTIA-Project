"""Explicación de cada resultado (capa 3, sección 6b).

Método de oclusión: para cada variable se reemplaza su valor por la mediana del entrenamiento 
y se mide cuánto baja la probabilidad de alerta. Las tres variables que más la bajan son los
"patrones detectados".
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .schema import TEXTO_FACTOR


def factores_principales(bundle: dict[str, Any], vector: dict[str, float], k: int = 3) -> list[dict]:
    features = bundle["features"]
    modelo = bundle["modelos"]["y_alerta"]
    base_fila = pd.DataFrame([vector])[features]
    base = float(modelo.predict_proba(base_fila)[0, 1])

    contribuciones = []
    for f in features:
        alterada = base_fila.copy()
        alterada[f] = bundle["medianas"][f]
        p = float(modelo.predict_proba(alterada)[0, 1])
        contribuciones.append((f, base - p))

    contribuciones.sort(key=lambda t: t[1], reverse=True)
    return [
        {"factor": f, "texto": TEXTO_FACTOR.get(f, f), "peso": round(max(delta, 0.0), 3)}
        for f, delta in contribuciones[:k]
        if round(delta, 3) > 0
    ]
