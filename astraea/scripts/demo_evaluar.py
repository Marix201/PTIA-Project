"""Evalúa una paciente simulada con el modelo entrenado y muestra el JSON de la API.
"""
import json
import sys

import numpy as np

import _ruta  # noqa: F401
from astraea.model import cargar
from astraea.servicio import evaluar
from astraea.synthetic import generar_paciente

grupo = sys.argv[1] if len(sys.argv) > 1 else "endo"
semilla = int(sys.argv[2]) if len(sys.argv) > 2 else 7
perfil, registros = generar_paciente(np.random.default_rng(semilla), grupo)
bundle = cargar(str(_ruta.RAIZ / "models" / "modelo.joblib"))
print(f"Paciente simulada del grupo '{grupo}' ({len(registros)} días de registro)")
print(json.dumps(evaluar(bundle, perfil, registros), indent=2, ensure_ascii=False))
