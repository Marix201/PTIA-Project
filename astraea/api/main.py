from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from astraea.model import cargar
from astraea.schema import (
    DX_PREVIOS,
    FAM_VALORES,
    MEDICACION,
    MIN_DIAS,
    SANGRADO,
    SINTOMAS_GI_URIN,
    TIPOS_DOLOR,
    UBICACIONES,
)
from astraea.servicio import evaluar

RAIZ = Path(__file__).resolve().parent.parent


def ruta_modelo() -> Path:
    return Path(os.environ.get("ASTRAEA_MODELO", RAIZ / "models" / "modelo.joblib"))


class RegistroDia(BaseModel):
    dolor: int = Field(ge=0, le=10, description="Intensidad del dolor, 0 a 10")
    ubic: list[Literal[UBICACIONES]] = []
    tipo: list[Literal[TIPOS_DOLOR]] = []
    en_periodo: bool = Field(description="¿El dolor coincide con el periodo?")
    sangrado: int = Field(ge=0, le=len(SANGRADO) - 1, description="0 ninguno ... 4 abundante")
    fatiga: int = Field(ge=0, le=10)
    gi: list[Literal[SINTOMAS_GI_URIN]] = []


class Perfil(BaseModel):
    fam: Literal[FAM_VALORES]
    dx: list[Literal[DX_PREVIOS]] = []
    med: list[Literal[MEDICACION]] = []
    ca125: Optional[float] = Field(default=None, ge=0, description="Opcional, en U/mL")
    edad: int = Field(ge=18, le=55)
    menarquia_edad: int = Field(ge=8, le=18)


class Solicitud(BaseModel):
    perfil: Perfil
    registros: list[RegistroDia] = Field(min_length=MIN_DIAS)


app = FastAPI(title="Astraea", version="0.1.0", description="Tamizaje de endometriosis y adenomiosis (prueba de concepto).")


@lru_cache(maxsize=1)
def _bundle(ruta: str):
    return cargar(ruta)


@app.get("/salud")
def salud():
    existe = ruta_modelo().exists()
    return {"estado": "ok" if existe else "sin_modelo", "modelo": str(ruta_modelo())}


@app.post("/evaluar")
def post_evaluar(solicitud: Solicitud):
    ruta = ruta_modelo()
    if not ruta.exists():
        raise HTTPException(503, "No hay modelo entrenado. Ejecuta: python scripts/entrenar.py")
    perfil = solicitud.perfil.model_dump()
    registros = [r.model_dump() for r in solicitud.registros]
    return evaluar(_bundle(str(ruta)), perfil, registros)
