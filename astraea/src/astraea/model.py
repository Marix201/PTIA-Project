"""Motor de clasificación (componente principal, sección 6e).

Entrena tres clasificadores binarios independientes:
  * y_alerta: señal de alerta general (endometriosis O adenomiosis frente a otra causa/ninguna)
  * y_endo:   compatibilidad con endometriosis
  * y_adeno:  compatibilidad con adenomiosis
Como son independientes, las dos compatibilidades no suman 100 % y pueden coexistir.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from .schema import FEATURES, FEATURES_PERFIL, TARGETS

VERSION = "0.1.0"
SENSIBILIDAD_OBJETIVO = 0.85
FAMILIAS = ("regresion_logistica", "arbol", "bosque", "boosting")


def crear_modelo(familia: str, seed: int = 42) -> Pipeline:
    """Pipeline completo (imputación + escalado + modelo) para evitar fuga de información."""
    imputador = SimpleImputer(strategy="median", keep_empty_features=True)
    if familia == "regresion_logistica":
        pasos = [
            ("imp", imputador),
            ("esc", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced", C=1.0)),
        ]
    elif familia == "arbol":
        pasos = [
            ("imp", imputador),
            (
                "clf",
                DecisionTreeClassifier(
                    max_depth=5, min_samples_leaf=20, class_weight="balanced", random_state=seed
                ),
            ),
        ]
    elif familia == "bosque":
        pasos = [
            ("imp", imputador),
            (
                "clf",
                RandomForestClassifier(
                    n_estimators=300,
                    min_samples_leaf=5,
                    class_weight="balanced_subsample",
                    n_jobs=-1,
                    random_state=seed,
                ),
            ),
        ]
    elif familia == "boosting":
        pasos = [
            ("imp", imputador),
            (
                "clf",
                HistGradientBoostingClassifier(
                    max_depth=3, learning_rate=0.08, max_iter=200, random_state=seed
                ),
            ),
        ]
    else:
        raise ValueError(f"Familia desconocida: {familia}")
    return Pipeline(pasos)


def ece(y: np.ndarray, p: np.ndarray, bins: int = 10) -> float:
    """Error de calibración esperado."""
    y, p = np.asarray(y), np.asarray(p)
    bordes = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lo, hi in zip(bordes[:-1], bordes[1:]):
        m = (p >= lo) & ((p < hi) if hi < 1 else (p <= hi))
        if m.any():
            total += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(total)


def sens_espec(y: np.ndarray, p: np.ndarray, umbral: float) -> tuple[float, float]:
    pred = p >= umbral
    y = np.asarray(y).astype(bool)
    sens = (pred & y).sum() / max(y.sum(), 1)
    espec = (~pred & ~y).sum() / max((~y).sum(), 1)
    return float(sens), float(espec)


def elegir_umbral(y: np.ndarray, p: np.ndarray, sens_min: float = SENSIBILIDAD_OBJETIVO) -> float:
    """Mayor umbral (más especificidad) que mantiene sensibilidad >= sens_min."""
    for u in np.unique(np.round(p, 4))[::-1]:
        if sens_espec(y, p, u)[0] >= sens_min:
            return float(u)
    return 0.0


def comparar_familias(X: pd.DataFrame, y: pd.Series, seed: int = 42, folds: int = 5) -> pd.DataFrame:
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=seed)
    filas = []
    for fam in FAMILIAS:
        aucs = cross_val_score(crear_modelo(fam, seed), X, y, cv=cv, scoring="roc_auc")
        filas.append({"familia": fam, "auc_cv_media": aucs.mean(), "auc_cv_sd": aucs.std()})
    return pd.DataFrame(filas).sort_values("auc_cv_media", ascending=False).reset_index(drop=True)


@dataclass
class Resultado:
    bundle: dict[str, Any]
    comparacion: dict[str, pd.DataFrame]
    metricas: dict[str, dict[str, float]]


def entrenar(
    df: pd.DataFrame,
    features: list[str] | None = None,
    seed: int = 42,
    test_size: float = 0.20,
) -> Resultado:
    features = list(features or FEATURES)
    train, test = train_test_split(df, test_size=test_size, stratify=df["grupo"], random_state=seed)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)

    modelos, comparacion, metricas, familias = {}, {}, {}, {}
    umbral_alerta = 0.5
    for objetivo in TARGETS:
        Xtr, ytr = train[features], train[objetivo]
        Xte, yte = test[features], test[objetivo]
        tabla = comparar_familias(Xtr, ytr, seed)
        comparacion[objetivo] = tabla
        mejor = tabla.loc[0, "familia"]
        familias[objetivo] = mejor

        calibrado = CalibratedClassifierCV(crear_modelo(mejor, seed), method="sigmoid", cv=5)
        calibrado.fit(Xtr, ytr)
        modelos[objetivo] = calibrado

        if objetivo == "y_alerta":
            oof = cross_val_predict(
                CalibratedClassifierCV(crear_modelo(mejor, seed), method="sigmoid", cv=5),
                Xtr,
                ytr,
                cv=cv,
                method="predict_proba",
            )[:, 1]
            umbral_alerta = elegir_umbral(ytr.to_numpy(), oof)
        umbral = umbral_alerta if objetivo == "y_alerta" else 0.5

        p = calibrado.predict_proba(Xte)[:, 1]
        sens, espec = sens_espec(yte.to_numpy(), p, umbral)
        metricas[objetivo] = {
            "familia": mejor,
            "umbral": umbral,
            "auc": float(roc_auc_score(yte, p)),
            "sensibilidad": sens,
            "especificidad": espec,
            "f1": float(f1_score(yte, p >= umbral)),
            "brier": float(brier_score_loss(yte, p)),
            "ece": ece(yte.to_numpy(), p),
            "n_prueba": int(len(yte)),
        }

    bundle = {
        "version": VERSION,
        "features": features,
        "modelos": modelos,
        "umbral_alerta": umbral_alerta,
        "medianas": train[features].median().to_dict(),
        "metricas": metricas,
        "semilla": seed,
        "datos": {
            "n": int(len(df)),
            "sinteticos": True,
            "huella": hashlib.sha256(pd.util.hash_pandas_object(df[features], index=False).values.tobytes()).hexdigest()[:16],
        },
    }
    return Resultado(bundle=bundle, comparacion=comparacion, metricas=metricas)


def ablacion(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Qué aporta cada grupo de variables a la señal de alerta (justificación del proyecto)."""
    sin_ca = [f for f in FEATURES if f not in ("ca125", "ca125_faltante")]
    configuraciones = {
        "solo perfil": FEATURES_PERFIL,
        "perfil + registro diario": FEATURES,
        "perfil + registro diario, sin laboratorio": sin_ca,
    }
    filas = []
    for nombre, cols in configuraciones.items():
        r = entrenar(df, features=cols, seed=seed)
        m = r.metricas["y_alerta"]
        filas.append(
            {
                "configuración": nombre,
                "familia": m["familia"],
                "auc": m["auc"],
                "sensibilidad": m["sensibilidad"],
                "especificidad": m["especificidad"],
            }
        )
    return pd.DataFrame(filas)


def guardar(bundle: dict[str, Any], ruta: str) -> None:
    joblib.dump(bundle, ruta)


def cargar(ruta: str) -> dict[str, Any]:
    return joblib.load(ruta)


def predecir(bundle: dict[str, Any], vector: dict[str, float]) -> dict[str, float]:
    """Probabilidades calibradas {y_alerta, y_endo, y_adeno} para un vector de variables."""
    fila = pd.DataFrame([vector])[bundle["features"]]
    return {t: float(bundle["modelos"][t].predict_proba(fila)[0, 1]) for t in TARGETS}
