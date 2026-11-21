"""Matrices de confusión y curvas de calibración del modelo entrenado (conjunto de prueba).

Uso (desde astraea/, después de scripts/entrenar.py):
    python scripts/figuras_metricas.py

Reproduce la misma partición que `entrenar` (misma semilla y estratificación) y usa los umbrales
guardados en el modelo. Escribe docs/figuras/matrices_confusion.png y docs/figuras/calibracion.png.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.calibration import calibration_curve  # noqa: E402

import _ruta  # noqa: E402
from astraea.model import cargar, particion, predecir  # noqa: E402
from astraea.rules import nivel_alerta  # noqa: E402
from astraea.schema import TARGETS  # noqa: E402

NOMBRES = {"y_alerta": "Señal de alerta", "y_endo": "Endometriosis", "y_adeno": "Adenomiosis"}

bundle = cargar(str(_ruta.RAIZ / "models" / "modelo.joblib"))
df = pd.read_csv(_ruta.RAIZ / "data" / "sintetico.csv")
_, test = particion(df, bundle["semilla"])
um = bundle["umbrales"]

X = test[bundle["features"]]
p = {t: bundle["modelos"][t].predict_proba(X)[:, 1] for t in TARGETS}
salida = _ruta.RAIZ / "docs" / "figuras"
salida.mkdir(exist_ok=True)

# --- Matrices de confusión: las tres etiquetas con su umbral, más la regla combinada ---
paneles = [(NOMBRES[t], test[t].to_numpy().astype(bool), p[t] >= um[t], um[t]) for t in TARGETS]
combinada = np.array(
    [
        nivel_alerta(a, um["y_alerta"], e, d, um["y_endo"], um["y_adeno"]) == "alta"
        for a, e, d in zip(p["y_alerta"], p["y_endo"], p["y_adeno"])
    ]
)
paneles.append(("Regla combinada", test["y_alerta"].to_numpy().astype(bool), combinada, None))

fig, ejes = plt.subplots(1, 4, figsize=(15, 4.6))
for ax, (titulo, y, pred, u) in zip(ejes, paneles):
    m = np.array([[(~y & ~pred).sum(), (~y & pred).sum()], [(y & ~pred).sum(), (y & pred).sum()]])
    ax.imshow(m, cmap="Purples")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, int(m[i, j]), ha="center", va="center", color="white" if m[i, j] > m.max() / 2 else "black", fontsize=13)
    sens = m[1, 1] / max(m[1].sum(), 1)
    espec = m[0, 0] / max(m[0].sum(), 1)
    ax.set_xticks([0, 1], ["Sin alerta", "Alerta"])
    ax.set_yticks([0, 1], ["No tiene", "Tiene"])
    ax.set_title(f"{titulo}\n" + (f"umbral {u:.2f}\n" if u is not None else "tres umbrales\n") + f"sens. {sens:.2f} · espec. {espec:.2f}", fontsize=10)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Real")
fig.suptitle(f"Matrices de confusión, conjunto de prueba (n = {len(test)}, datos sintéticos)")
fig.tight_layout()
fig.savefig(salida / "matrices_confusion.png", dpi=150)
plt.close(fig)

# --- Curvas de calibración (diagrama de fiabilidad) ---
fig, ejes = plt.subplots(1, 3, figsize=(13, 4))
for ax, t in zip(ejes, TARGETS):
    frac, media = calibration_curve(test[t], p[t], n_bins=8, strategy="quantile")
    ax.plot([0, 1], [0, 1], "--", color="gray", label="Calibración perfecta")
    ax.plot(media, frac, "o-", color="#4b3fa0", label="Modelo")
    ax.set_title(NOMBRES[t])
    ax.set_xlabel("Probabilidad predicha")
    ax.set_ylabel("Proporción observada")
    ax.legend(loc="upper left", fontsize=8)
fig.suptitle("Calibración en el conjunto de prueba (datos sintéticos)")
fig.tight_layout()
fig.savefig(salida / "calibracion.png", dpi=150)
plt.close(fig)
print(f"Figuras en {salida}")
