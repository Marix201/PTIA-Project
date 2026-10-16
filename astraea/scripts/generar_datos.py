"""Genera el conjunto SINTÉTICO de entrenamiento: data/sintetico.csv
"""
import sys

import _ruta  # noqa: F401
from astraea.synthetic import GRUPOS, generar

n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
semilla = int(sys.argv[2]) if len(sys.argv) > 2 else 42
df = generar(n, semilla)
destino = _ruta.RAIZ / "data" / "sintetico.csv"
df.to_csv(destino, index=False)
print(f"{len(df)} filas guardadas en {destino}")
print(df["grupo"].value_counts().reindex(GRUPOS).to_string())
print("Recordatorio: datos sintéticos, no son pacientes reales.")
