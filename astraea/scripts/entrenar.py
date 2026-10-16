"""Entrena el modelo, lo guarda en models/modelo.joblib y escribe un reporte de resultados.
"""
import json
import sys

import pandas as pd

import _ruta  # noqa: F401
from astraea.model import ablacion, entrenar, guardar
from astraea.synthetic import generar

n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
semilla = int(sys.argv[2]) if len(sys.argv) > 2 else 42
csv = _ruta.RAIZ / "data" / "sintetico.csv"
df = pd.read_csv(csv) if csv.exists() else None
if df is None or len(df) != n:
    df = generar(n, semilla)
    df.to_csv(csv, index=False)

res = entrenar(df, seed=semilla)
(_ruta.RAIZ / "models").mkdir(exist_ok=True)
guardar(res.bundle, str(_ruta.RAIZ / "models" / "modelo.joblib"))
(_ruta.RAIZ / "models" / "metricas.json").write_text(
    json.dumps(res.metricas, indent=2, ensure_ascii=False), encoding="utf-8"
)

abl = ablacion(df, seed=semilla)

def tabla(d: pd.DataFrame) -> str:
    return d.round(3).to_markdown(index=False) if hasattr(d, "to_markdown") else d.round(3).to_string(index=False)

try:
    import tabulate  # noqa: F401
except ImportError:
    tabla = lambda d: "```\n" + d.round(3).to_string(index=False) + "\n```"  # noqa: E731

lineas = [
    "# Resultados preliminares (datos SINTÉTICOS)",
    "",
    "Estas métricas miden si el pipeline recupera las asociaciones que el equipo asumió al generar los datos,",
    "no la capacidad clínica del modelo. No deben presentarse como evidencia clínica.",
    "",
    f"Filas: {len(df)}. Semilla: {semilla}. Conjunto de prueba: 20 %, estratificado por grupo.",
    "",
]
for obj, tab in res.comparacion.items():
    lineas += [f"## Comparación de modelos, validación cruzada de 5 particiones: {obj}", "", tabla(tab), ""]
lineas += ["## Métricas en el conjunto de prueba (modelo elegido y calibrado)", ""]
met = pd.DataFrame(res.metricas).T.reset_index().rename(columns={"index": "etiqueta"})
lineas += [tabla(met), ""]
lineas += ["## Ablación sobre la señal de alerta", "", tabla(abl), ""]
destino = _ruta.RAIZ / "docs" / "RESULTADOS_PRELIMINARES.md"
destino.write_text("\n".join(lineas), encoding="utf-8")

print(met.round(3).to_string(index=False))
print()
print(abl.round(3).to_string(index=False))
print(f"\nModelo en models/modelo.joblib; reporte en {destino}")
